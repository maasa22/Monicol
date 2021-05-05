<template>
  <div>
    <div v-for="date in date_list" :key="date.index">
      <h1>{{ date }}</h1>
      <div v-for="time in time_list" :key="time.index">
        <v-btn>{{ time }}</v-btn>
      </div>
    </div>
  </div>
</template>

<script>
// import utils from "@/plugins/utils";
export default {
  // smixins: [utils],
  data() {
    return {
      date_list: [],
      time_list: [
        "8:00 ~ 8:10",
        "8:10 ~ 8:20",
        "8:20 ~ 8:30",
        "8:30 ~ 8:40",
        "8:40 ~ 8:50",
        "8:50 ~ 9:00"
      ]
    };
  },
  methods: {
    formatDate(time) {
      let year = ("0000" + time.getFullYear()).slice(-4);
      let month = ("00" + String(Number(time.getMonth()) + 1)).slice(-2);
      let date = ("00" + time.getDate()).slice(-2);
      let formatDate = year + "/" + month + "/" + date;
      return formatDate;
    }
  },
  mounted() {
    // let today = new Date();
    // let today_format = this.formatDate(today);
    // this.date_list.push(today_format);
    for (let i = 1; i < 4; i++) {
      let today = new Date();
      let day = new Date();
      day.setDate(today.getDate() + i);
      let day_format = this.formatDate(day);
      this.date_list.push(day_format);
    }
  }
};
</script>
