import axios from "axios";

const API_BASE_URL = "https://dobrin.xyz/api";
export default {
    login(company, username, password) {
        return axios.post(`${API_BASE_URL}/login`, { company, username, password });
    },

    fetchSchedule(userId) {
        return axios.get(`${API_BASE_URL}/schedule/${userId}`);
    },

    googleLogin() {
        window.location.href = `${API_BASE_URL}/auth/login`;
    },

    syncCalendarOAuth(accessToken, shifts) {
        return axios.post(`${API_BASE_URL}/sync-calendar-oauth`, {
            access_token: accessToken,
            shifts: shifts
        });
    },

    generateEventLink(shift) {
        const baseUrl = "https://www.google.com/calendar/event?action=TEMPLATE";

        const formattedDate = shift.date.replace(/-/g, '');

        const startDateTime = `${formattedDate}T${shift.planned_start.replace(/:/g, '')}`;
        const endDateTime = `${formattedDate}T${shift.planned_end.replace(/:/g, '')}`;

        const title = encodeURIComponent(`Shift - ${shift.role_name}`);

        return `${baseUrl}&dates=${startDateTime}/${endDateTime}&text=${title}&location=&details=Shift+scheduled`;
    }
};
