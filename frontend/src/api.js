import axios from "axios";

const API_BASE_URL = "https://shift2calendar.onrender.com";

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
