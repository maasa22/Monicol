<template>
  <div>
    <div v-for="date in date_list" :key="date.index">
      <h3>{{ date }}</h3>
      <v-container>
        <v-row class="grey lighten-3">
          <v-col
            xs="6"
            sm="4"
            md="2"
            lg="2"
            xl="2"
            v-for="time in time_list"
            :key="time.index"
          >
            <v-btn color="primary"> {{ time }}</v-btn>
          </v-col>
        </v-row>
      </v-container>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      date_list: [],
      time_list: [
        "7:00 ~ 7:10",
        "7:10 ~ 7:20",
        "7:20 ~ 7:30",
        "7:30 ~ 7:40",
        "7:40 ~ 7:50",
        "7:50 ~ 8:00",
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
      // let formatDate = year + "/" + month + "/" + date;
      let formatDate = year + "/" + month + "/" + date;
      return formatDate;
    }
  },
  mounted() {
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
