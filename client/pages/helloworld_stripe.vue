<template>
  <div>
    <h2>Payment Methods</h2>
    <details id="add-new-card">
      <summary>Add new</summary>
      <form id="payment-method-form" @submit.prevent="addNewCard">
        <label>
          氏名
          <input type="text" name="name" required v-model="name" />
        </label>
        <fieldset>
          <div id="card-element"></div>
        </fieldset>
        <div id="error-message" role="alert"></div>
        <p><input type="submit" value="submit" /></p>
      </form>
    </details>
    <hr />
    <form id="payment-form">
      <div>
        <label>
          Card:
          <select name="payment-method" required>
            <option
              id="cardOption.id"
              value="cardOption.value"
              text="cardOption.text"
              v-for="cardOption in cardOptions"
              :key="cardOption.index"
            >
              {{ cardOption.text }}
            </option>
          </select>
        </label>
      </div>
    </form>
    <div style="height:100px"></div>
    <div id="firebaseui-auth-container"></div>
    <v-btn @click="signout">sign out</v-btn>
  </div>
</template>

<script>
import firebase from "~/plugins/firebase";

export default {
  data() {
    return {
      name: "",
      customerData: {},
      currentUser: {},
      cardElement: "",
      test_cards: [
        4242424242424242,
        5555555555554444,
        2223003122003222,
        4000056655665556
      ],
      cardOptions: []
    };
  },
  methods: {
    // 書き直せばわんちゃん直るかな...？ form もあんまり使ったことないし。 コピペミスもありえるし。
    async addNewCard(event) {
      if (!event.target.reportValidity()) {
        return;
      }
      const form = new FormData(event.target);
      const cardholderName = form.get("name");

      console.log(this.customerData.setup_secret);
      console.log(this.cardElement);
      console.log(cardholderName);
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
      ); // should catch error
      console.log(setupIntent);
      console.log(setupIntent.setupIntent);
      console.log(setupIntent.setupIntent.payment_method);
      await firebase
        .firestore()
        .collection("stripe_customers")
        .doc(this.currentUser.uid)
        .collection("payment_methods")
        //.add({ id: setupIntent.payment_method });
        .add({ id: setupIntent.setupIntent.payment_method });
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
            // console.log(this.cardOptions);
            // console.log(this.currentUser);

            cardOptions.push({
              id: `card-${doc.id}`,
              value: paymentMethod.id,
              text: `${paymentMethod.card.brand} •••• ${paymentMethod.card.last4} | Expires ${paymentMethod.card.exp_month}/${paymentMethod.card.exp_year}`
            });

            // const optionId = `card-${doc.id}`;
            // let optionElement = document.getElementById(optionId);
            // console.log(optionId);

            // // Add a new option if one doesn't exist yet.
            // if (!optionElement) {
            //   optionElement = document.createElement("option");
            //   optionElement.id = optionId;
            //   document
            //     .querySelector("select[name=payment-method]")
            //     .appendChild(optionElement);
            // }

            // optionElement.value = paymentMethod.id;
            // optionElement.text = `${paymentMethod.card.brand} •••• ${paymentMethod.card.last4} | Expires ${paymentMethod.card.exp_month}/${paymentMethod.card.exp_year}`;
          });
        });
      return cardOptions;
    },
    signout() {
      firebase.auth().signOut();
    }
  },
  mounted() {
    var firebaseui = require("firebaseui");
    const firebaseUI = new firebaseui.auth.AuthUI(firebase.auth());
    const firebaseUiConfig = {
      callbacks: {
        signInSuccessWithAuthResult: function(authResult, redirectUrl) {
          // User successfully signed in.
          // Return type determines whether we continue the redirect automatically
          // or whether we leave that to developer to handle.
          return true;
        },
        uiShown: () => {
          //   document.getElementById("loader").style.display = "none";
        }
      },
      signInFlow: "popup",
      signInSuccessUrl: "/helloworld_stripe",
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
        console.log(currentUser.uid);
        // console.log(
        //   firebase
        //     .firestore()
        //     .collection("stripe_customers")
        //     .doc(currentUser.uid)
        // );
        firebase
          .firestore()
          .collection("stripe_customers")
          .doc(currentUser.uid)
          .onSnapshot(snapshot => {
            // console.log(snapshot);
            // console.log(snapshot.data());
            if (snapshot.data()) {
              this.customerData = snapshot.data();
              //   console.log("cusomerData-------------------", this.customerData);
              this.cardOptions = this.startDataListeners();
              //   document.getElementById("loader").style.display = "none";
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
