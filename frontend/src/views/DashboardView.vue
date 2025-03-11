<template>
    <div class="dashboard-container">
      <h2>Welcome to Your Shift Dashboard</h2>
      <button @click="fetchSchedule">Load My Shifts</button>
      <button @click="syncCalendar">Sync to Google Calendar</button>
  
      <ul v-if="shifts.length">
        <li v-for="shift in shifts" :key="shift.date">
          {{ shift.date }} - {{ shift.planned_start }} to {{ shift.planned_end }}
        </li>
      </ul>
      <p v-if="message">{{ message }}</p>
    </div>
  </template>
  
  <script>
  import api from "../api.js";
  
  export default {
    data() {
      return {
        userId: localStorage.getItem("user_id"),
        shifts: [],
        message: "",
      };
    },
    methods: {
      async fetchSchedule() {
        try {
          const response = await api.fetchSchedule(this.userId);
          this.shifts = response.data;
          this.message = "Shifts loaded!";
        } catch (error) {
          this.message = "Failed to load shifts.";
        }
      },
      async syncCalendar() {
        try {
          await api.syncCalendar(this.userId);
          this.message = "Shifts synced to Google Calendar!";
        } catch (error) {
          this.message = "Failed to sync shifts.";
        }
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
  