<template>
  <div>
    <div id="card-element"></div>
    <div style="height:100px"></div>
    <div id="firebaseui-auth-container"></div>
    <v-btn @click="signout">sign out</v-btn>
  </div>
</template>

<script>
import firebase from "~/plugins/firebase";

export default {
  data() {
    return {};
  },
  methods: {
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
      signInSuccessUrl: "/",
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
        console.log(currentUser.uid);
        firebase
          .firestore()
          .collection("stripe_customers")
          .doc(currentUser.uid)
          .onSnapshot(snapshot => {
            console.log(snapshot);
            console.log(snapshot.data());
            if (snapshot.data()) {
              console.log("hoge3");
              let customerData = snapshot.data();
              //   startDataListeners();
              //   document.getElementById("loader").style.display = "none";
              //   document.getElementById("content").style.display = "block";
            } else {
              console.log("hoge4");
              //   console.warn(
              //     `No Stripe customer found in Firestore for user: ${currentUser.uid}`
              //   );
            }
          });
      } else {
        // document.getElementById("content").style.display = "none";
        firebaseUI.start("#firebaseui-auth-container", firebaseUiConfig);
      }
    });
    if (this.$stripe) {
      const stripe = this.$stripe; // stripe is now available!!
      const elements = stripe.elements();
      const card = elements.create("card", {});
      // Add an instance of the card Element into the `card-element` <div>
      card.mount("#card-element");
    }
  }
};
</script>
