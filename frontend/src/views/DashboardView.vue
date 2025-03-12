<template>
  <div class="dashboard-container">
    <h2>My Shifts</h2>
    <button @click="fetchSchedule">📅 Load My Shifts</button>

    <ul v-if="shifts.length">
      <li v-for="shift in shifts" :key="shift.date">
        {{ shift.date }} - {{ shift.planned_start }} to {{ shift.planned_end }}
        <a :href="generateEventLink(shift)" target="_blank">📅 Add to Google Calendar</a>
      </li>
    </ul>
    <button v-if="!accessToken" @click="googleLogin">🔗 Log in with Google to add all shifts</button>
    <button v-if="shifts.length && accessToken" @click="syncShifts">📅 Add All Shifts to Google Calendar</button>
  </div>
</template>

<script>
import api from "../api.js";

export default {
  data() {
    return {
      userId: localStorage.getItem("user_id") || "",
      accessToken: localStorage.getItem("access_token") || "",
      shifts: []
    };
  },
  created() {
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get("access_token");
    if (token) {
      localStorage.setItem("access_token", token);
      this.accessToken = token;
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  },
  methods: {
    async fetchSchedule() {
      try {
        const response = await api.fetchSchedule(this.userId);
        this.shifts = response.data;
      } catch (error) {
        alert("Failed to load shifts.");
      }
    },
    async syncShifts() {
      if (!this.accessToken) {
        alert("Please log in with Google first.");
        return;
      }

      try {
        await api.syncCalendarOAuth(this.accessToken, this.shifts);
        alert("Shifts added to Google Calendar!");
      } catch (error) {
        alert("Failed to sync shifts.");
      }
    },
    generateEventLink(shift) {
      return api.generateEventLink(shift);
    },
    googleLogin() {
      api.googleLogin();
    }
  }
};
</script>
