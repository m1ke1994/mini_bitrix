<template>
  <AppShell>
    <section class="page">
      <h1>Заявки</h1>
      <p v-if="error" class="error">{{ error }}</p>

      <div class="filters">
        <select v-model="statusFilter" @change="loadLeads">
          <option value="">Все статусы</option>
          <option value="new">Новая</option>
          <option value="in_progress">В работе</option>
          <option value="closed">Закрыта</option>
        </select>
        <input v-model="dateFrom" type="date" @change="loadLeads" />
        <input v-model="dateTo" type="date" @change="loadLeads" />
      </div>

      <table class="table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Имя</th>
            <th>Телефон</th>
            <th>Статус</th>
            <th>Создано</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="lead in leads" :key="lead.id">
            <td>{{ lead.id }}</td>
            <td>{{ lead.name }}</td>
            <td>{{ lead.phone }}</td>
            <td>
              <select :value="lead.status" @change="changeStatus(lead.id, $event.target.value)">
                <option value="new">Новая</option>
                <option value="in_progress">В работе</option>
                <option value="closed">Закрыта</option>
              </select>
            </td>
            <td>{{ lead.created_at }}</td>
          </tr>
        </tbody>
      </table>

      <div class="pagination">
        <button :disabled="!prevPage" @click="goPage(prevPage)">Назад</button>
        <button :disabled="!nextPage" @click="goPage(nextPage)">Вперед</button>
      </div>
    </section>
  </AppShell>
</template>

<script setup>
import { onMounted, ref } from "vue";
import AppShell from "../components/AppShell.vue";
import api from "../services/api";

const leads = ref([]);
const error = ref("");
const nextPage = ref("");
const prevPage = ref("");
const statusFilter = ref("");
const dateFrom = ref("");
const dateTo = ref("");
const currentPath = ref("/api/leads/");

function buildParams() {
  const params = {};
  if (statusFilter.value) params.status = statusFilter.value;
  if (dateFrom.value) params.date_from = dateFrom.value;
  if (dateTo.value) params.date_to = dateTo.value;
  return params;
}

async function loadLeads(url = "/api/leads/") {
  currentPath.value = url;
  error.value = "";
  try {
    const isAbsolute = url.startsWith("http");
    const response = isAbsolute ? await api.get(url) : await api.get(url, { params: buildParams() });
    leads.value = response.data.results || [];
    nextPage.value = response.data.next || "";
    prevPage.value = response.data.previous || "";
  } catch (_) {
    error.value = "Ошибка загрузки заявок.";
  }
}

async function changeStatus(id, status) {
  try {
    await api.patch(`/api/leads/${id}/status/`, { status });
    await loadLeads(currentPath.value);
  } catch (_) {
    error.value = "Ошибка обновления статуса.";
  }
}

function goPage(url) {
  if (url) loadLeads(url);
}

onMounted(() => loadLeads());
</script>
