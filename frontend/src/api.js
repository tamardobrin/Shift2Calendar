import axios from "axios";

// Set the FastAPI backend URL
const API_BASE_URL = "http://127.0.0.1:8000";

export default {
  login(company, username, password) {
    return axios.post(`${API_BASE_URL}/login`, {
      company,
      username,
      password,
    });
  },

  fetchSchedule(userId) {
    return axios.get(`${API_BASE_URL}/schedule/${userId}`);
  },

  syncCalendar(userId) {
    return axios.post(`${API_BASE_URL}/sync-calendar/${userId}`);
  },
};
