<template>
  <div class="login-container">
    <h2>🔐 Login</h2>

    <form @submit.prevent="shiftLogin">
      <input v-model="company" type="text" placeholder="Company ID" required />
      <input v-model="username" type="text" placeholder="Username" required />
      <input v-model="password" type="password" placeholder="Password" required />
      <button type="submit" class="btn btn-primary">🔑 Log in to Shift Organizer</button>
    </form>

    <p v-if="loginMessage" class="error-message">{{ loginMessage }}</p>
  </div>
</template>

<script>
import api from "../api.js";

export default {
  data() {
    return {
      company: "",
      username: "",
      password: "",
      loginMessage: "",
    };
  },
  methods: {
    async shiftLogin() {
      try {
        const response = await api.login(this.company, this.username, this.password);
        localStorage.setItem("user_id", response.data.user_id);
        this.$router.push("/dashboard");
      } catch (error) {
        this.loginMessage = "Login failed! Check your credentials.";
      }
    }
  }
};
</script>

<style>
/* Responsive Styling */
.login-container {
  max-width: 400px;
  margin: 80px auto;
  padding: 20px;
  background: white;
  border-radius: 10px;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
  text-align: center;
}

h2 {
  color: #333;
}

form {
  display: flex;
  flex-direction: column;
}

input {
  padding: 12px;
  margin: 8px 0;
  border-radius: 5px;
  border: 1px solid #ddd;
  font-size: 16px;
}

.error-message {
  color: red;
  font-size: 14px;
  margin-top: 10px;
}

.btn {
  padding: 12px 16px;
  margin-top: 10px;
  border: none;
  cursor: pointer;
  font-size: 16px;
  border-radius: 5px;
  transition: all 0.3s ease-in-out;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn:hover {
  opacity: 0.85;
}

/* Responsive Fixes */
@media (max-width: 768px) {
  .login-container {
    width: 90%;
  }
}
</style>
