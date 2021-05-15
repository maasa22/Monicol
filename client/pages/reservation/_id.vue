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
      <div>
        <p>{{ reservation.datetime }}</p>
        <p>
          この日時にあなたの電話番号に電話をかけさせていただきます。良い朝をお迎えください。
        </p>
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
      loaded: false,
      loadUnit: 20,
      reservation: {},
      reservationId: null
    };
  },
  methods: {
    async fetchReservation(reservationdId) {
      console.log(reservationdId);
      await firebase
        .firestore()
        .collection("reservations")
        .doc(this.currentUser.uid)
        .collection("each_reservation")
        .doc(reservationdId)
        .get()
        .then(doc => {
          if (doc.exists) {
            console.log("Document data:", doc.data());
            let reservation = doc.data();
            reservation.reservationId = doc.id;
            this.reservation = reservation;
          } else {
            // doc.data() will be undefined in this case
            console.log("No such document!");
          }
        })
        .catch(error => {
          console.log("Error getting document:", error);
        });
    },
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
        let reservationId = this.$route.params.id;
        this.reservationId = reservationId;
        this.fetchReservation(reservationId);
        this.loaded = true;
      } else {
        this.loaded = false;
        firebaseUI.start("#firebaseui-auth-container", firebaseUiConfig);
      }
    });
  }
};
</script>

<style scoped></style>
