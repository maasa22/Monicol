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
            <nuxt-link
              :to="{
                path:
                  '/time/' +
                  date.slice(0, 4) +
                  '_' +
                  date.slice(5, 7) +
                  '_' +
                  date.slice(8, 10) +
                  '_' +
                  time.slice(0, 2) +
                  '_' +
                  time.slice(3, 5)
              }"
            >
              <v-btn color="primary"> {{ time }}</v-btn>
            </nuxt-link>
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
        "07:00 ~ 07:10",
        "07:10 ~ 07:20",
        "07:20 ~ 07:30",
        "07:30 ~ 07:40",
        "07:40 ~ 07:50",
        "07:50 ~ 08:00",
        "08:00 ~ 08:10",
        "08:10 ~ 08:20",
        "08:20 ~ 08:30",
        "08:30 ~ 08:40",
        "08:40 ~ 08:50",
        "08:50 ~ 09:00"
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
    // 明日以降の予約ができる。 improvement: 前日の21時までにする。
    for (let i = 1; i < 9; i++) {
      let today = new Date();
      let day = new Date();
      day.setDate(today.getDate() + i);
      let day_format = this.formatDate(day);
      this.date_list.push(day_format);
    }
    // improvement: 空き枠がある所だけにする。
  }
};
</script>
