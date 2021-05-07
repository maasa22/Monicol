<template>
  <div>
    <div class="login_widget">
      <div id="firebaseui-auth-container"></div>
      <v-btn @click="signout">sign out</v-btn>
    </div>
    <div v-show="!loaded">
      Loading &hellip;
    </div>
    <section id="content" v-show="loaded">
      <div class="summary">
        <h3>予約時間</h3>
        <p>2021/05/06</p>
        <p>08:20</p>
      </div>
      <h3>支払い方法の選択</h3>
      <details id="add-new-card">
        <summary>支払い方法の追加</summary>
        <form id="payment-method-form" @submit.prevent="addNewCard">
          <label>
            カード名義
            <input
              type="text"
              name="cardholderName"
              required
              v-model="cardholderName"
            />
          </label>
          <fieldset>
            <div id="card-element"></div>
          </fieldset>
          <div id="error-message" role="alert"></div>
          <p><input type="submit" value="追加" /></p>
        </form>
      </details>
      {{ error_message }}

      <v-btn color="primary">支払う</v-btn>
    </section>
  </div>
</template>

<script>
import firebase from "~/plugins/firebase";

export default {
  data() {
    return {
      currentUser: null, // loing user info
      cardOptions: [],
      cardholderName: null,
      error_message: "",
      loaded: false
    };
  },
  methods: {
    // 書き直せばわんちゃん直るかな...？ form もあんまり使ったことないし。 コピペミスもありえるし。
    async addNewCard(event) {
      if (!event.target.reportValidity()) {
        return;
      }
      const form = new FormData(event.target);
      const cardholderName = form.get("cardholderName");

      console.log(this.customerData.setup_secret);
      console.log(this.cardElement);
      console.log(cardholderName);
      try {
        const setupIntent = await this.$stripe.confirmCardSetup(
          this.customerData.setup_secret,
          {
            payment_method: {
              card: this.cardElement,
              billing_details: {
                name: cardholderName
              }
            }
          }
        );
        await firebase
          .firestore()
          .collection("stripe_customers")
          .doc(this.currentUser.uid)
          .collection("payment_methods")
          .add({ id: setupIntent.setupIntent.payment_method });
      } catch (err) {
        alert(err); // replace alert into "this.error_message=xxx"
      }
    },
    // listen する系は、computed とかなのかも知れぬ... async とかを入れると良いのかも？
    /**
     * Set up Firestore data listeners
     */
    startDataListeners() {
      /**
       * Get all payment methods for the logged in customer
       */
      let cardOptions = [];
      console.log(this.currentUser);
      console.log(this.cardOptions);
      firebase
        .firestore()
        .collection("stripe_customers")
        .doc(this.currentUser.uid)
        .collection("payment_methods")
        .onSnapshot(snapshot => {
          if (snapshot.empty) {
            // document.querySelector("#add-new-card").open = true;
          }
          snapshot.forEach(function(doc) {
            const paymentMethod = doc.data();
            if (!paymentMethod.card) {
              return;
            }

            // this がここで効かなくなる...
            // Add a new option if one doesn't exist yet.
            const targetList = cardOptions.filter(cardOption => {
              return cardOption.id === `card-${doc.id}`;
            });

            if (targetList.length === 0) {
              cardOptions.push({
                id: `card-${doc.id}`,
                value: paymentMethod.id,
                text: `${paymentMethod.card.brand} •••• ${paymentMethod.card.last4} | Expires ${paymentMethod.card.exp_month}/${paymentMethod.card.exp_year}`
              });
            }
          });
        });
      return cardOptions;
    },
    // Create payment form
    async createPaymentForm(event) {
      const form = new FormData(event.target);
      const amount = Number(form.get("amount"));
      const currency = form.get("currency");
      const data = {
        payment_method: form.get("payment-method"),
        currency,
        amount: this.formatAmountForStripe(amount, currency),
        status: "new"
      };

      await firebase
        .firestore()
        .collection("stripe_customers")
        .doc(this.currentUser.uid)
        .collection("payments")
        .add(data);
    },
    signout() {
      firebase.auth().signOut();
    },
    // Format amount for Stripe
    formatAmountForStripe(amount, currency) {
      return this.zeroDecimalCurrency(amount, currency)
        ? amount
        : Math.round(amount * 100);
    },
    // Check if we have a zero decimal currency
    // https://stripe.com/docs/currencies#zero-decimal
    zeroDecimalCurrency(amount, currency) {
      let numberFormat = new Intl.NumberFormat(["en-US"], {
        style: "currency",
        currency: currency,
        currencyDisplay: "symbol"
      });
      const parts = numberFormat.formatToParts(amount);
      let zeroDecimalCurrency = true;
      for (let part of parts) {
        if (part.type === "decimal") {
          zeroDecimalCurrency = false;
        }
      }
      return zeroDecimalCurrency;
    }
  },
  mounted() {
    /**
     * Firebase auth configuration
     */
    var firebaseui = require("firebaseui");
    const firebaseUI =
      new firebaseui.auth.AuthUI(firebase.auth()) ||
      firebaseui.auth.AuthUI.getInstance();
    const firebaseUiConfig = {
      callbacks: {
        signInSuccessWithAuthResult: function(authResult, redirectUrl) {
          // User successfully signed in.
          // Return type determines whether we continue the redirect automatically
          // or whether we leave that to developer to handle.
          return true;
        },
        uiShown: () => {
          this.loaded = true;
        }
      },
      signInFlow: "popup",
      signInSuccessUrl: "/time",
      signInOptions: [
        {
          provider: firebase.auth.GoogleAuthProvider.PROVIDER_ID
        },
        {
          provider: firebase.auth.EmailAuthProvider.PROVIDER_ID,
          requireDisplayName: false
        }
      ],
      credentialHelper: firebaseui.auth.CredentialHelper.NONE,
      // Your terms of service url.
      tosUrl: "https://example.com/terms",
      // Your privacy policy url.
      privacyPolicyUrl: "https://example.com/privacy"
    };
    firebase.auth().onAuthStateChanged(firebaseUser => {
      if (firebaseUser) {
        const currentUser = firebaseUser;
        this.currentUser = currentUser;
        firebase
          .firestore()
          .collection("stripe_customers")
          .doc(currentUser.uid)
          .onSnapshot(snapshot => {
            if (snapshot.data()) {
              this.customerData = snapshot.data();
              this.cardOptions = this.startDataListeners();
              this.loaded = true;
              //   document.getElementById("content").style.display = "block";
            } else {
              console.warn(
                `No Stripe customer found in Firestore for user: ${currentUser.uid}`
              );
            }
          });
      } else {
        // document.getElementById("content").style.display = "none";
        firebaseUI.start("#firebaseui-auth-container", firebaseUiConfig);
      }
    });
    /**
     * Set up Stripe Elements
     */
    // show card-element
    if (this.$stripe) {
      const stripe = this.$stripe; // stripe is now available!!
      const elements = stripe.elements();
      const cardElement = elements.create("card", {
        hidePostalCode: true
      });
      // Add an instance of the card Element into the `card-element` <div>
      cardElement.mount("#card-element");
      this.cardElement = cardElement;
    }
  }
};
</script>

<style scoped>
.summary {
  margin: 20px auto;
}
</style>
