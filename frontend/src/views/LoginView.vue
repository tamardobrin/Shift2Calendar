<template>
  <div class="login-container">
    <h2>Login</h2>

    <form @submit.prevent="shiftLogin">
      <input v-model="company" type="text" placeholder="Company ID" required />
      <input v-model="username" type="text" placeholder="Username" required />
      <input v-model="password" type="password" placeholder="Password" required />
      <button type="submit">🔑 Log in to Shift Organizer</button>
    </form>

    <p v-if="loginMessage">{{ loginMessage }}</p>

    <hr />
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
