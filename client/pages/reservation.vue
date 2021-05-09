<template>
  <div>
    <div class="login_widget">
      <div id="firebaseui-auth-container"></div>
      <!-- <v-btn @click="signout">sign out</v-btn> -->
    </div>
    <div>予約一覧</div>
    <div v-show="!loaded">
      Loading &hellip;
    </div>
    <section id="content" v-show="loaded">
      hogehoge
    </section>
  </div>
</template>

<script>
import firebase from "~/plugins/firebase";

export default {
  data() {
    return {
      currentUser: null, // loing user info
      loaded: false
    };
  },
  methods: {
    signout() {
      firebase.auth().signOut();
    }
  },
  mounted() {
    /**
     * Firebase auth configuration
     */
    var firebaseui = require("firebaseui");
    let firebaseUI = firebaseui.auth.AuthUI.getInstance();
    if (!firebaseUI) {
      firebaseUI = new firebaseui.auth.AuthUI(firebase.auth());
    }
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
      } else {
        this.loaded = false;
        firebaseUI.start("#firebaseui-auth-container", firebaseUiConfig);
      }
    });
  }
};
</script>

<style scoped></style>
