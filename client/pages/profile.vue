<template>
  <div>
    <div class="login_widget">
      <div id="firebaseui-auth-container"></div>
      <!-- <v-btn @click="signout">sign out</v-btn> -->
    </div>
    <h1>プロフィール</h1>
    <div v-show="!loaded">
      Loading &hellip;
    </div>
    <section id="content" v-show="loaded">
      <v-container class="grey lighten-5">
        <v-row>
          <v-col cols="6" sm="6" md="6" lg="6" xl="6" class="profile_key">
            ニックネーム
          </v-col>
          <v-col cols="6" sm="6" md="6" lg="6" xl="6" class="profile_value">
            value
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="6" sm="6" md="6" lg="6" xl="6" class="profile_key">
            電話番号
          </v-col>
          <v-col cols="6" sm="6" md="6" lg="6" xl="6" class="profile_value">
            value
          </v-col>
        </v-row>
      </v-container>
      <h4>自己紹介</h4>
      <p>value</p>
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
        this.loaded = true;
      } else {
        this.loaded = false;
        firebaseUI.start("#firebaseui-auth-container", firebaseUiConfig);
      }
    });
  }
};
</script>

<style scoped>
#content {
  padding: 0px 10px;
}
.profile_key {
  text-align: left;
}
.profile_value {
  text-align: right;
}
</style>
