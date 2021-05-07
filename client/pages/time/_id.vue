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
      <div>
        <h3>支払い</h3>
        <form id="payment-form" @submit.prevent="createPaymentForm">
          <div class="payment-card">
            <label>
              支払い方法:
              <select name="payment-method" required>
                <option
                  v-for="cardOption in cardOptions"
                  :key="cardOption.index"
                  :id="cardOption.id"
                  :value="cardOption.value"
                  :text="cardOption.text"
                >
                  {{ cardOption.text }}
                </option>
              </select>
              <!-- <v-select
                :items="cardOptions"
                item-text="text"
                item-value="value"
                required
              ></v-select> -->
            </label>
          </div>
          <div>150円</div>
          <!-- <div>
            <label>
              金額:
              <input
                name="amount"
                type="number"
                min="1"
                max="99999999"
                value="100"
                required
              />
            </label>
            <label>
              Currency:
              <select name="currency">
                <option value="jpy">JPY</option>
                <option value="usd">USD</option>
                <option value="eur">EUR</option>
                <option value="gbp">GBP</option>
              </select>
            </label>
          </div> -->
          <!-- <v-btn color="primary">支払う</v-btn> -->
          <input type="submit" value="支払う" />
        </form>
        <details id="add-new-card" :open="isShowingCard">
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
            <div id="error-message" role="alert">{{ error_message }}</div>
            <p><input type="submit" value="追加" /></p>
          </form>
        </details>
      </div>
      <div>
        <h3>支払い履歴</h3>
        <ul id="payments-list" v-for="payment in payments" :key="payment.index">
          <li>{{ payment.amount }}円支払いました</li>
        </ul>
      </div>
    </section>
  </div>
</template>

<script>
import firebase from "~/plugins/firebase";

export default {
  data() {
    return {
      currentUser: null, // loing user info
      customerData: {},
      cardOptions: [],
      payments: [],
      cardholderName: null,
      error_message: "",
      loaded: false,
      isShowingCard: false
    };
  },
  methods: {
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
    getAllPaymentMethods() {
      /**
       * Get all payment methods for the logged in customer
       */
      let cardOptions = [];
      //   console.log(this.currentUser);
      //   console.log(this.cardOptions);
      firebase
        .firestore()
        .collection("stripe_customers")
        .doc(this.currentUser.uid)
        .collection("payment_methods")
        .onSnapshot(snapshot => {
          if (snapshot.empty) {
            this.isShowingCard = true;
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
    getAllPayments() {
      /**
       * Get all payments for the logged in customer
       */
      // need to modify
      let payments = [];
      firebase
        .firestore()
        .collection("stripe_customers")
        .doc(this.currentUser.uid)
        .collection("payments")
        .onSnapshot(snapshot => {
          snapshot.forEach(doc => {
            const payment = doc.data();

            const targetList = payments.filter(payment => {
              return payment.id === `payment-${doc.id}`;
            });

            let content = "";
            if (
              payment.status === "new" ||
              payment.status === "requires_confirmation"
            ) {
              content = `Creating Payment for ${this.formatAmount(
                payment.amount,
                payment.currency
              )}`;
            } else if (payment.status === "succeeded") {
              const card = payment.charges.data[0].payment_method_details.card;
              content = `✅ Payment for ${this.formatAmount(
                payment.amount,
                payment.currency
              )} on ${card.brand} card •••• ${card.last4}.`;
            } else if (payment.status === "requires_action") {
              content = `🚨 Payment for ${this.formatAmount(
                payment.amount,
                payment.currency
              )} ${payment.status}`;
              this.handleCardAction(payment, doc.id);
            } else {
              content = `⚠️ Payment for ${this.formatAmount(
                payment.amount,
                payment.currency
              )} ${payment.status}`;
            }

            if (targetList.length === 0) {
              payments.push(payment);
            }
          });
        });
      return payments;
    },
    // Handle card actions like 3D Secure
    async handleCardAction(payment, docId) {
      const { error, paymentIntent } = await stripe.handleCardAction(
        payment.client_secret
      );
      if (error) {
        alert(error.message);
        payment = error.payment_intent; // let が必要な気がする？
      } else if (paymentIntent) {
        payment = paymentIntent; // let が必要な気がする？
      }

      await firebase
        .firestore()
        .collection("stripe_customers")
        .doc(this.currentUser.uid)
        .collection("payments")
        .doc(docId)
        .set(payment, { merge: true });
    },
    // Create payment form
    async createPaymentForm(event) {
      console.log("hogehoge");
      const form = new FormData(event.target);
      // const amount = Number(form.get("amount"));
      const amount = 150;
      // const currency = form.get("currency");
      const currency = "jpy";
      const data = {
        payment_method: form.get("payment-method"),
        currency,
        amount: this.formatAmountForStripe(amount, currency),
        status: "new"
      };
      console.log(data);
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
    // Format amount for diplay in the UI
    formatAmount(amount, currency) {
      amount = this.zeroDecimalCurrency(amount, currency)
        ? amount
        : (amount / 100).toFixed(2);
      return new Intl.NumberFormat("en-US", {
        style: "currency",
        currency
      }).format(amount);
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
      firebaseui.auth.AuthUI.getInstance(); // to prevent error
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
      tosUrl: "https://example.com/terms", // to be changed
      // Your privacy policy url.
      privacyPolicyUrl: "https://example.com/privacy" // to be changed
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
              this.cardOptions = this.getAllPaymentMethods();
              this.payments = this.getAllPayments();
              this.loaded = true;
              //   document.getElementById("content").style.display = "block";
            } else {
              console.warn(
                `No Stripe customer found in Firestore for user: ${currentUser.uid}`
              );
            }
          });
      } else {
        this.loaded = false;
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
      cardElement.on("change", ({ error }) => {
        if (error) {
          this.error_message = error.message;
        } else {
          this.error_message = "";
        }
      });
      this.cardElement = cardElement;
    }
  }
};
</script>

<style scoped>
.summary {
  margin: 20px auto 50px;
}
#add-new-card {
  margin: 10px auto 20px;
}
.payment-card {
  margin: 8px auto 8px;
}
</style>
