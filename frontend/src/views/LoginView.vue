<template>
    <div class="login-container">
      <h2>Login to Shift Organizer</h2>
      <form @submit.prevent="handleLogin">
        <input v-model="company" type="text" placeholder="Company ID" required />
        <input v-model="username" type="text" placeholder="Username" required />
        <input v-model="password" type="password" placeholder="Password" required />
        <button type="submit">Login</button>
      </form>
      <p v-if="message">{{ message }}</p>
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
        message: "",
      };
    },
    methods: {
      async handleLogin() {
        try {
          const response = await api.login(this.company, this.username, this.password);
          this.message = response.data.message;
          localStorage.setItem("user_id", response.data.user_id);
          this.$router.push("/dashboard"); // Redirect after login
        } catch (error) {
          this.message = "Login failed!";
        }
      }
    }
  };
  </script>
  
  <style scoped>
  .login-container {
    max-width: 300px;
    margin: auto;
    text-align: center;
  }
  input {
    display: block;
    width: 100%;
    margin: 10px 0;
    padding: 8px;
  }
  button {
    padding: 8px;
    background: blue;
    color: white;
    border: none;
    cursor: pointer;
  }
  </style>
  