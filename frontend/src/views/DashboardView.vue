<template>
  <div class="dashboard-container">
    <h2>📅 My Shifts</h2>

    <button @click="fetchSchedule" class="btn btn-primary">
      🔄 Load My Shifts
    </button>

    <div v-if="shifts.length" class="shift-list">
      <ul>
        <li v-for="shift in shifts" :key="shift.date" class="shift-item">
          <div class="shift-details">
            <strong>{{ shift.date }}</strong> 
            ({{ shift.planned_start }} - {{ shift.planned_end }})
          </div>
          <a :href="generateEventLink(shift)" target="_blank" class="btn btn-link">
            📅 Add to Google Calendar
          </a>
        </li>
      </ul>
    </div>

    <div class="button-group">
      <button v-if="!accessToken" @click="googleLogin" class="btn btn-secondary">
        🔗 Log in with Google to add all shifts
      </button>

      <button v-if="shifts.length && accessToken" @click="syncShifts" class="btn btn-success">
        📅 Add All Shifts to Google Calendar
      </button>
    </div>
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

<style>
body {
  font-family: Arial, sans-serif;
  background-color: #f4f4f4;
  margin: 0;
  padding: 0;
}

.dashboard-container {
  max-width: 800px; 
  margin: 40px auto;
  padding: 20px;
  background: white;
  border-radius: 10px;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
  text-align: center;
}

h2 {
  color: #333;
}

.btn {
  display: inline-block;
  padding: 12px 16px;
  margin: 10px;
  border: none;
  cursor: pointer;
  font-size: 16px;
  border-radius: 6px;
  transition: all 0.3s ease-in-out;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-success {
  background-color: #28a745;
  color: white;
}

.btn-link {
  color: #007bff;
  text-decoration: none;
}

.btn:hover {
  opacity: 0.85;
}

.button-group {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  margin-top: 20px;
}

.shift-list {
  margin-top: 20px;
}

.shift-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fafafa;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 10px;
  box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1);
  text-align: left;
}

@media (max-width: 768px) {
  .dashboard-container {
    width: 90%;
  }
  .shift-item {
    flex-direction: column;
    text-align: center;
  }
}
</style>
