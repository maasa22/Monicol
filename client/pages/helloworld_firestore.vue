<template>
  <div>
    <div id="loader">Loading &hellip;</div>
    <p>hoge</p>
    <button @click="addData">add data to firestore</button>
  </div>
</template>

<script>
import firebase from "~/plugins/firebase";

export default {
  data() {
    return {
      variable1: "hoge1",
      variable2: "hoge2"
    };
  },
  methods: {
    async addData() {
      const data = {
        var1: "hoge1",
        var2: "hoge2"
      };
      const res = await firebase
        .firestore()
        .collection("tests")
        .doc("hogehoge")
        .set(data);
    }
  }
};
</script>

<style></style>
