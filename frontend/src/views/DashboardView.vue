<template>
  <div class="dashboard-container">
    <h2>Welcome to Your Shift Dashboard</h2>
    <button @click="fetchSchedule">Load My Shifts</button>

    <ul v-if="shifts.length">
      <li v-for="shift in shifts" :key="shift.date">
        {{ shift.date }} - {{ shift.planned_start }} to {{ shift.planned_end }}
        <a :href="generateEventLink(shift)" target="_blank">📅 Add to Google Calendar</a>
      </li>
    </ul>
  </div>
</template>

<script>
import api from "../api.js";

export default {
  data() {
    return {
      userId: localStorage.getItem("user_id"),
      shifts: [],
    };
  },
  methods: {
    async fetchSchedule() {
      try {
        const response = await api.fetchSchedule(this.userId);
        this.shifts = response.data;
      } catch (error) {
        console.error("Failed to load shifts.");
      }
    },
    generateEventLink(shift) {
      const baseUrl = "https://www.google.com/calendar/event?action=TEMPLATE";
      
      const formattedDate = shift.date.replace(/-/g, '');

      const startDateTime = `${formattedDate}T${shift.planned_start.replace(/:/g, '')}`;
      const endDateTime = `${formattedDate}T${shift.planned_end.replace(/:/g, '')}`;

      const title = encodeURIComponent(`Shift - ${shift.role_name}`);

      return `${baseUrl}&dates=${startDateTime}/${endDateTime}&text=${title}&location=&details=Shift+scheduled`;
    }
  }
};
</script>

<style scoped>
.dashboard-container {
  max-width: 400px;
  margin: auto;
  text-align: center;
}
button {
  margin: 10px;
  padding: 8px;
  background: green;
  color: white;
  border: none;
  cursor: pointer;
}
</style>
