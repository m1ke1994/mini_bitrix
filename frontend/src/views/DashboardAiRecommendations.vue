<template>
  <section class="dashboard-section behavior-page">
    <nav class="dashboard-subnav behavior-tabs" aria-label="Разделы поведения пользователя">
      <a
        v-for="tab in behaviorTabItems"
        :key="tab.id"
        href="#"
        :class="{ active: activeBehaviorTab === tab.id }"
        @click.prevent="setActiveBehaviorTab(tab.id)"
      >
        {{ tab.label }}
      </a>
    </nav>

    <div v-if="activeBehaviorTab === 'behavior-overview'" class="chart-card">
      <div class="card-head">
        <h2>Поведение пользователя на сайте</h2>
      </div>
      <p class="muted">
        Раздел показывает, как посетители ведут себя на сайте: докуда доходят, где взаимодействуют с формами и кнопками,
        какие блоки просматривают и на каком этапе теряется интерес.
      </p>
    </div>

    <div v-if="activeBehaviorTab === 'behavior-overview'" class="chart-card behavior-ai-card">
      <div class="card-head card-head-wrap">
        <h2>AI-рекомендации по повышению конверсии</h2>
        <button
          type="button"
          class="ai-refresh-btn"
          :disabled="aiRecommendationsLoading"
          @click="refreshAiRecommendations"
        >
          {{ aiRecommendationsLoading ? "Обновление..." : "Обновить рекомендации" }}
        </button>
      </div>
      <p class="muted block-help">
        Короткая сводка по точкам роста: как упростить путь пользователя и повысить число заявок.
      </p>
      <p v-if="aiRecommendationsLoading" class="muted">Готовим рекомендации...</p>
      <template v-else>
        <p class="ai-summary">{{ aiRecommendations.summary }}</p>
        <div class="ai-meta">
          <span class="status-badge" :class="`status-priority-${aiRecommendations.priority || 'medium'}`">
            Приоритет: {{ aiPriorityLabel(aiRecommendations.priority) }}
          </span>
          <span class="muted">{{ aiRecommendations.source === "ai" ? "Источник: AI" : "Источник: fallback" }}</span>
          <span v-if="aiRecommendations.cached" class="muted">Кэшированный ответ</span>
        </div>
        <ul v-if="aiRecommendations.items?.length" class="ai-items">
          <li v-for="(item, idx) in aiRecommendations.items" :key="`behavior-ai-item-${idx}`">{{ item }}</li>
        </ul>
        <p v-else class="muted">Пока нет готовых рекомендаций. Попробуйте обновить позже.</p>
        <p v-if="aiRecommendationsError" class="muted">{{ aiRecommendationsError }}</p>
      </template>
    </div>

    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="loading" class="muted loading-note">Обновление данных...</p>

    <div v-if="activeBehaviorTab === 'behavior-overview'" class="stats behavior-stats">
      <article class="stat-card">
        <h3>Уникальные пользователи в анализе</h3>
        <strong>{{ uniqueUsersInAnalysis }}</strong>
      </article>
      <article class="stat-card">
        <h3>Средняя глубина просмотра</h3>
        <strong>{{ formatPercent(avgScrollDepthValue) }}</strong>
      </article>
      <article class="stat-card">
        <h3>Начали заполнять форму</h3>
        <strong>{{ formStartedUsersValue }}</strong>
      </article>
      <article class="stat-card">
        <h3>Успешно отправили форму</h3>
        <strong>{{ formSubmitSuccessUsersValue }}</strong>
      </article>
      <article class="stat-card">
        <h3>Нажали на важные кнопки</h3>
        <strong>{{ ctaClickUsersValue }}</strong>
      </article>
      <article class="stat-card">
        <h3>Совершили полезные действия</h3>
        <strong>{{ microConversionUsersValue }}</strong>
      </article>
    </div>

    <div v-if="activeBehaviorTab === 'behavior-scroll'" class="chart-card">
      <div class="card-head">
        <h2>Глубина просмотра страницы</h2>
      </div>
      <p class="muted block-help">
        Метрика считается по уникальным пользователям. Каждый пользователь учитывается только один раз по максимальной
        достигнутой глубине просмотра.
      </p>
      <div class="scroll-overview">
        <article class="scroll-metric">
          <span class="muted">Средняя глубина просмотра</span>
          <strong>{{ formatPercent(scrollAvgDepth) }}</strong>
        </article>
        <article class="scroll-metric">
          <span class="muted">Уникальных пользователей в анализе</span>
          <strong>{{ scrollUniqueUsersTotal }}</strong>
        </article>
      </div>
      <div class="thresholds-grid">
        <article v-for="level in scrollLevels" :key="level" class="threshold-item">
          <span class="threshold-title">До {{ level }}% страницы дошли</span>
          <strong>{{ scrollThresholdUsers(level) }} из {{ scrollUniqueUsersTotal }}</strong>
          <span class="muted threshold-help">({{ formatPercent(scrollThresholdRate(level)) }})</span>
        </article>
      </div>
    </div>

    <div v-if="activeBehaviorTab === 'behavior-forms'" class="chart-card">
      <div class="card-head">
        <h2>События форм</h2>
      </div>
      <p class="muted block-help">Показывает количество событий на каждом шаге взаимодействия с формой за выбранный период.</p>
      <div class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>Событие</th>
              <th>Что означает</th>
              <th>Количество</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Форма в зоне видимости</td>
              <td class="muted">Пользователь увидел блок формы на экране.</td>
              <td>{{ formVisibleCount }}</td>
            </tr>
            <tr>
              <td>Начали заполнение</td>
              <td class="muted">Пользователь начал ввод данных в форму.</td>
              <td>{{ formStartedCount }}</td>
            </tr>
            <tr>
              <td>Заполнили первое поле</td>
              <td class="muted">Сделан первый реальный шаг заполнения формы.</td>
              <td>{{ formFirstFieldCompletedCount }}</td>
            </tr>
            <tr>
              <td>Попытка отправки</td>
              <td class="muted">Пользователь нажал отправку формы.</td>
              <td>{{ formSubmitAttemptCount }}</td>
            </tr>
            <tr>
              <td>Успешная отправка</td>
              <td class="muted">Форма отправлена без ошибки.</td>
              <td>{{ formSubmitSuccessCount }}</td>
            </tr>
            <tr>
              <td>Ошибка отправки</td>
              <td class="muted">При отправке формы произошла ошибка.</td>
              <td>{{ formSubmitErrorCount }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="activeBehaviorTab === 'behavior-forms'" class="chart-card">
      <div class="card-head">
        <h2>Воронка формы</h2>
      </div>
      <p class="muted block-help">Показывает, сколько уникальных пользователей доходит до каждого шага формы.</p>
      <p v-if="showFormFunnelEmpty" class="muted">{{ blockEmptyReason(formFunnel, "Пока недостаточно данных для воронки формы.") }}</p>
      <div v-else class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>Этап</th>
              <th>Уникальные пользователи</th>
              <th>Переход к следующему шагу</th>
              <th>Доля от первого шага</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in formFunnelRows" :key="row.stage">
              <td>{{ formStageLabel(row.stage) }}</td>
              <td>{{ row.users || 0 }}</td>
              <td>{{ formatPercent(row.next_step_rate_pct) }}</td>
              <td>{{ formatPercent(row.from_first_step_pct) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="activeBehaviorTab === 'behavior-forms'" class="chart-card">
      <div class="card-head">
        <h2>Аналитика полей формы</h2>
      </div>
      <p class="muted block-help">
        Помогает увидеть проблемные поля: где пользователи чаще останавливаются, ошибаются или возвращаются к вводу.
      </p>
      <p v-if="showFieldAnalyticsEmpty" class="muted">
        {{ blockEmptyReason(fieldAnalytics, "Пока недостаточно данных по событиям полей формы.") }}
      </p>
      <template v-else>
        <div class="field-highlights">
          <span class="muted">Начали форму: <strong>{{ fieldSummary.form_started_users }}</strong></span>
          <span class="muted">Дошли до первого поля: <strong>{{ fieldSummary.first_field_completed_users }}</strong></span>
          <span class="muted">Столкнулись с ошибками: <strong>{{ fieldSummary.field_error_users }}</strong></span>
          <span class="muted">Первое поле старта: <strong>{{ firstFieldStartedLabel }}</strong></span>
          <span class="muted">Чаще останавливаются на: <strong>{{ topDropOffLabel }}</strong></span>
          <span class="muted">Больше ошибок на: <strong>{{ topErrorLabel }}</strong></span>
          <span class="muted">Чаще возвращаются к: <strong>{{ topRevisitLabel }}</strong></span>
        </div>
        <div class="table-wrap">
          <table class="table">
            <thead>
              <tr>
                <th>Поле</th>
                <th>Начали ввод</th>
                <th>Заполнили</th>
                <th>Ошибки</th>
                <th>Повторные возвраты</th>
                <th>Процент заполнения</th>
                <th>Остановились на этом поле</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in fieldRows" :key="row.field_key">
                <td>{{ fieldLabel(row) }}</td>
                <td>{{ row.started || 0 }}</td>
                <td>{{ row.completed || 0 }}</td>
                <td>{{ row.errors || 0 }}</td>
                <td>{{ row.revisits || 0 }}</td>
                <td>{{ formatPercent(row.completion_rate_pct) }}</td>
                <td>{{ row.drop_off || 0 }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
    </div>

    <div v-if="activeBehaviorTab === 'behavior-cta-sections'" class="chart-card">
      <div class="card-head">
        <h2>Эффективность кнопок</h2>
      </div>
      <p class="muted block-help">Показывает, какие кнопки реально приводят пользователей к целевому действию и заявке.</p>
      <p v-if="showCtaFunnelEmpty" class="muted">{{ blockEmptyReason(ctaFunnel, "Пока недостаточно данных по кнопкам.") }}</p>
      <div v-else class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>Кнопка</th>
              <th>Показы</th>
              <th>Клики</th>
              <th>Дошли до целевого действия</th>
              <th>Конверсии</th>
              <th>CTR кнопок</th>
              <th>Переход в заявку после клика</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in ctaRows" :key="row.cta_id">
              <td>{{ ctaLabel(row) }}</td>
              <td>{{ row.shows || 0 }}</td>
              <td>{{ row.clicks || 0 }}</td>
              <td>{{ row.target_reached || 0 }}</td>
              <td>{{ row.conversions || 0 }}</td>
              <td>{{ formatPercent(row.ctr_pct) }}</td>
              <td>{{ formatPercent(row.click_to_conversion_rate_pct) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="activeBehaviorTab === 'behavior-cta-sections'" class="chart-card">
      <div class="card-head">
        <h2>Аналитика секций</h2>
      </div>
      <p class="muted block-help">
        Показывает, как отдельные блоки сайта влияют на поведение: удержание внимания, переход к кнопкам и заявкам.
      </p>
      <p v-if="showSectionAnalyticsEmpty" class="muted">
        {{ blockEmptyReason(sectionAnalytics, "Пока недостаточно данных по просмотру секций.") }}
      </p>
      <div v-else class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>Секция</th>
              <th>Просмотры</th>
              <th>Среднее время</th>
              <th>Клик по кнопкам после секции</th>
              <th>Начали форму после секции</th>
              <th>Конверсии после секции</th>
              <th>Остановились после секции</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in sectionRows" :key="row.section_id">
              <td>{{ row.section_name || row.section_id }}</td>
              <td>{{ row.views || 0 }}</td>
              <td>{{ formatSeconds(row.avg_time_spent_seconds) }}</td>
              <td>{{ row.cta_after_section || 0 }}</td>
              <td>{{ row.form_start_after_section || 0 }}</td>
              <td>{{ row.conversions_after_section || 0 }}</td>
              <td>{{ formatPercent(row.exit_after_section_rate_pct) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="activeBehaviorTab === 'behavior-segmentation'" class="chart-card">
      <div class="card-head">
        <h2>Сегментация по источникам</h2>
      </div>
      <p class="muted block-help">Показывает, какие источники дают более качественную аудиторию по пользователям и конверсии.</p>
      <p v-if="showSourceSegmentationEmpty" class="muted">
        {{ blockEmptyReason(sourceSegmentation, "Пока недостаточно данных для сегментации по источникам.") }}
      </p>
      <div v-else class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>Источник</th>
              <th>Пользователи</th>
              <th>Доля пользователей</th>
              <th>Сессии</th>
              <th>Средняя глубина просмотра</th>
              <th>CTR кнопок</th>
              <th>Начали форму</th>
              <th>Успешные отправки</th>
              <th>Конверсия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in sourceRows" :key="row.source">
              <td>{{ sourceLabel(row.source) }}</td>
              <td>{{ row.users || 0 }}</td>
              <td>{{ formatPercent(row.users_share_pct) }}</td>
              <td>{{ row.sessions || 0 }}</td>
              <td>{{ formatPercent(row.avg_scroll_depth) }}</td>
              <td>{{ formatPercent(row.cta_ctr_pct) }}</td>
              <td>{{ row.form_starts || 0 }}</td>
              <td>{{ row.form_submit_success || 0 }}</td>
              <td>{{ formatPercent(row.conversion_rate_pct) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="activeBehaviorTab === 'behavior-segmentation'" class="chart-card">
      <div class="card-head">
        <h2>Сегментация по устройствам</h2>
      </div>
      <p class="muted block-help">Показывает различия поведения пользователей на десктопе, мобильных и планшетах.</p>
      <p v-if="showDeviceSegmentationEmpty" class="muted">
        {{ blockEmptyReason(deviceSegmentation, "Пока недостаточно данных для сегментации по устройствам.") }}
      </p>
      <div v-else class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>Устройство</th>
              <th>Пользователи</th>
              <th>Доля пользователей</th>
              <th>Сессии</th>
              <th>Клики по кнопкам</th>
              <th>Начали форму</th>
              <th>Успешные отправки</th>
              <th>Конверсия формы</th>
              <th>Средняя глубина просмотра</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in deviceRows" :key="row.device">
              <td>{{ deviceLabel(row.device) }}</td>
              <td>{{ row.users || 0 }}</td>
              <td>{{ formatPercent(row.users_share_pct) }}</td>
              <td>{{ row.sessions || 0 }}</td>
              <td>{{ row.cta_clicks || 0 }}</td>
              <td>{{ row.form_starts || 0 }}</td>
              <td>{{ row.form_submit_success || 0 }}</td>
              <td>{{ formatPercent(row.form_conversion_rate_pct) }}</td>
              <td>{{ formatPercent(row.avg_scroll_depth) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="activeBehaviorTab === 'behavior-micro'" class="chart-card">
      <div class="card-head">
        <h2>Полезные действия на сайте</h2>
      </div>
      <p class="muted block-help">
        Отражает действия, которые показывают вовлечённость: клики по контактам, карте, FAQ, видео и другим важным
        элементам.
      </p>
      <p v-if="showMicroConversionsEmpty" class="muted">
        {{ blockEmptyReason(microConversions, "Пока нет полезных действий от посетителей.") }}
      </p>
      <div v-else class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>Действие</th>
              <th>Количество</th>
              <th>Уникальные пользователи</th>
              <th>Чаще всего на странице</th>
              <th>Связанная секция</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in microRows" :key="row.event">
              <td>{{ microLabel(row) }}</td>
              <td>{{ row.count || 0 }}</td>
              <td>{{ row.unique_users || 0 }}</td>
              <td>{{ row.page || "—" }}</td>
              <td>{{ row.section || "—" }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="activeBehaviorTab === 'behavior-changes' && showAnomaliesTable" class="chart-card">
      <div class="card-head">
        <h2>Изменения за период</h2>
      </div>
      <p class="muted block-help">Сравнение текущего периода с предыдущим. Помогает увидеть резкие изменения в поведении.</p>
      <div class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>Метрика</th>
              <th>Текущее значение</th>
              <th>Предыдущее значение</th>
              <th>Изменение</th>
              <th>Статус</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in anomalyRowsComparable" :key="row.metric">
              <td>{{ row.label || row.metric }}</td>
              <td>{{ row.current_value ?? 0 }}</td>
              <td>{{ row.previous_value ?? 0 }}</td>
              <td>{{ formatSignedPercent(row.change_pct) }}</td>
              <td>
                <span class="status-badge" :class="anomalyStatusClass(row.status)">
                  {{ anomalyStatusLabel(row.status) }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-else-if="activeBehaviorTab === 'behavior-changes' && showAnomaliesCompact" class="chart-card compact-note">
      <div class="card-head">
        <h2>Изменения за период</h2>
      </div>
      <p class="muted">{{ anomaliesReason }}</p>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";

import { useAiRecommendations } from "../composables/useAiRecommendations";
import { useAnalyticsSummary } from "../composables/useAnalyticsSummary";

const { summary, error, loading, loadSummary } = useAnalyticsSummary();
const {
  recommendations: aiRecommendations,
  loading: aiRecommendationsLoading,
  error: aiRecommendationsError,
  loadAiRecommendations,
} = useAiRecommendations({
  endpoint: "/api/analytics/ai-recommendations/",
  fallbackTitle: "Рекомендации временно недоступны",
  fallbackSummary: "Не удалось получить AI-анализ по поведенческим данным. Попробуйте позже.",
});

const behaviorTabItems = [
  { id: "behavior-overview", label: "Обзор" },
  { id: "behavior-scroll", label: "Глубина просмотра" },
  { id: "behavior-forms", label: "Формы" },
  { id: "behavior-cta-sections", label: "Кнопки и секции" },
  { id: "behavior-segmentation", label: "Сегментация" },
  { id: "behavior-micro", label: "Полезные действия" },
  { id: "behavior-changes", label: "Изменения" },
];

const activeBehaviorTab = ref("behavior-overview");

const aiSignals = computed(() => summary.value.ai_event_signals || {});
const overview = computed(() => aiSignals.value.overview || {});
const scrollSignals = computed(() => aiSignals.value.scroll_depth || {});
const formSignals = computed(() => aiSignals.value.forms || {});

const formVisibleCount = computed(() => Number(formSignals.value.form_visible || formSignals.value.form_view || 0));
const formStartedCount = computed(() => Number(formSignals.value.form_started || formSignals.value.form_start || 0));
const formFirstFieldCompletedCount = computed(() =>
  Number(formSignals.value.form_first_field_completed || formSignals.value.form_first_field_filled || 0)
);
const formSubmitAttemptCount = computed(() => Number(formSignals.value.form_submit_attempt || 0));
const formSubmitSuccessCount = computed(() => Number(formSignals.value.form_submit_success || 0));
const formSubmitErrorCount = computed(() => Number(formSignals.value.form_submit_error || 0));

const formFunnel = computed(() => aiSignals.value.form_funnel || { has_data: false, rows: [] });
const fieldAnalytics = computed(() => aiSignals.value.field_analytics || { has_data: false, rows: [] });
const ctaFunnel = computed(() => aiSignals.value.cta_funnel || { has_data: false, rows: [] });
const sectionAnalytics = computed(() => aiSignals.value.section_analytics || { has_data: false, rows: [] });
const deviceSegmentation = computed(() => aiSignals.value.device_segmentation || { has_data: false, rows: [] });
const sourceSegmentation = computed(() => aiSignals.value.source_segmentation || { has_data: false, rows: [] });
const microConversions = computed(() => aiSignals.value.micro_conversions || { has_data: false, rows: [] });
const anomalies = computed(() => aiSignals.value.anomalies || { has_data: false, rows: [] });

const formFunnelRows = computed(() => formFunnel.value.rows || []);
const fieldRows = computed(() => fieldAnalytics.value.rows || []);
const ctaRows = computed(() => ctaFunnel.value.rows || []);
const sectionRows = computed(() => sectionAnalytics.value.rows || []);
const deviceRows = computed(() => deviceSegmentation.value.rows || []);
const sourceRows = computed(() => sourceSegmentation.value.rows || []);
const microRows = computed(() => microConversions.value.rows || []);
const anomalyRows = computed(() => anomalies.value.rows || []);
const anomalyRowsComparable = computed(() => anomalyRows.value.filter((row) => !row.insufficient_data));

const fieldSummary = computed(() => fieldAnalytics.value.summary || {});
const anomaliesReason = computed(() => anomalies.value.insufficient_data_reason || "Недостаточно данных для сравнения.");

const showFormFunnelEmpty = computed(() => !loading.value && (!formFunnel.value.has_data || !formFunnelRows.value.length));
const showFieldAnalyticsEmpty = computed(() => !loading.value && (!fieldAnalytics.value.has_data || !fieldRows.value.length));
const showCtaFunnelEmpty = computed(() => !loading.value && (!ctaFunnel.value.has_data || !ctaRows.value.length));
const showSectionAnalyticsEmpty = computed(() =>
  !loading.value && (!sectionAnalytics.value.has_data || !sectionRows.value.length)
);
const showDeviceSegmentationEmpty = computed(() =>
  !loading.value && (!deviceSegmentation.value.has_data || !deviceRows.value.length)
);
const showSourceSegmentationEmpty = computed(() =>
  !loading.value && (!sourceSegmentation.value.has_data || !sourceRows.value.length)
);
const showMicroConversionsEmpty = computed(() =>
  !loading.value && (!microConversions.value.has_data || !microRows.value.length)
);

const showAnomaliesTable = computed(() => !loading.value && anomalyRowsComparable.value.length > 0);
const showAnomaliesCompact = computed(
  () => !loading.value && !showAnomaliesTable.value && Boolean(anomaliesReason.value)
);

const scrollLevels = [25, 50, 75, 100];

const scrollUniqueUsersTotal = computed(() => Number(scrollSignals.value.unique_users_total || 0));
const scrollAvgDepth = computed(() => Number(scrollSignals.value.avg_scroll_depth || 0));

const uniqueUsersInAnalysis = computed(() =>
  Number(overview.value.unique_users_total || scrollSignals.value.unique_users_total || 0)
);
const avgScrollDepthValue = computed(() => Number(overview.value.avg_scroll_depth || scrollSignals.value.avg_scroll_depth || 0));

const formStartedUsersValue = computed(() =>
  Number(overview.value.form_started_users || formStageUsers("form_started"))
);
const formSubmitSuccessUsersValue = computed(() =>
  Number(overview.value.form_submit_success_users || formStageUsers("form_submit_success"))
);
const ctaClickUsersValue = computed(() => Number(overview.value.cta_click_users || 0));
const microConversionUsersValue = computed(() => {
  const explicitValue = Number(overview.value.micro_conversion_users || 0);
  if (explicitValue > 0) return explicitValue;
  return microRows.value.reduce((sum, row) => sum + Number(row.unique_users || 0), 0);
});

const firstFieldStartedLabel = computed(() => {
  const item = fieldAnalytics.value.first_field_starts?.[0];
  if (!item) return "—";
  return `${item.field_name || "поле"}${item.form_id ? ` (${item.form_id})` : ""}`;
});

const topDropOffLabel = computed(() => {
  const item = fieldAnalytics.value.top_drop_off_field;
  if (!item) return "—";
  return `${item.field_name || "поле"} (${item.count || 0})`;
});

const topErrorLabel = computed(() => {
  const item = fieldAnalytics.value.top_error_field;
  if (!item) return "—";
  return `${item.field_name || "поле"} (${item.count || 0})`;
});

const topRevisitLabel = computed(() => {
  const item = fieldAnalytics.value.top_revisit_field;
  if (!item) return "—";
  return `${item.field_name || "поле"} (${item.count || 0})`;
});

function formStageUsers(stage) {
  const row = formFunnelRows.value.find((item) => item.stage === stage);
  return Number(row?.users || 0);
}

function scrollThresholdUsers(level) {
  return Number(
    scrollSignals.value.threshold_users?.[String(level)] ??
      scrollSignals.value.threshold_users?.[level] ??
      scrollSignals.value.thresholds?.[String(level)] ??
      scrollSignals.value.thresholds?.[level] ??
      0
  );
}

function scrollThresholdRate(level) {
  const explicitRate =
    scrollSignals.value.threshold_rates_pct?.[String(level)] ?? scrollSignals.value.threshold_rates_pct?.[level];
  if (explicitRate !== undefined && explicitRate !== null) {
    return Number(explicitRate || 0);
  }
  const total = scrollUniqueUsersTotal.value;
  if (!total) return 0;
  return (scrollThresholdUsers(level) / total) * 100;
}

function blockEmptyReason(block, fallbackText) {
  const reason = block?.insufficient_data_reason;
  if (reason) return reason;
  return fallbackText;
}

function formStageLabel(stage) {
  const labels = {
    form_visible: "Увидели форму",
    form_started: "Начали заполнение",
    form_first_field_completed: "Заполнили первое поле",
    form_submit_attempt: "Попытались отправить форму",
    form_submit_success: "Успешно отправили форму",
    form_submit_error: "Ошибка отправки",
  };
  return labels[stage] || stage;
}

function fieldLabel(row) {
  if (!row) return "—";
  const name = row.field_name || "поле";
  const type = row.field_type || "unknown";
  const formId = row.form_id || "form";
  return `${name} (${type}, ${formId})`;
}

function ctaLabel(row) {
  if (!row) return "—";
  if (row.cta_text) {
    return `${row.cta_text}${row.cta_type ? ` (${row.cta_type})` : ""}`;
  }
  return `${row.cta_id || "cta"}${row.cta_type ? ` (${row.cta_type})` : ""}`;
}

function microLabel(row) {
  if (!row) return "—";
  return row.label || row.event || "действие";
}

function sourceLabel(source) {
  const labels = {
    organic: "Органический трафик",
    paid: "Платный трафик",
    social: "Соцсети",
    direct: "Прямые заходы",
    referral: "Переходы с других сайтов",
    email: "Email",
    unknown: "Не определён",
  };
  return labels[source] || source || "—";
}

function deviceLabel(device) {
  const labels = {
    desktop: "Десктоп",
    mobile: "Мобильный",
    tablet: "Планшет",
    unknown: "Не определено",
  };
  return labels[device] || device || "—";
}

function formatPercent(value) {
  const normalized = Number(value || 0);
  return `${normalized.toFixed(2)}%`;
}

function formatSignedPercent(value) {
  const normalized = Number(value || 0);
  const sign = normalized > 0 ? "+" : "";
  return `${sign}${normalized.toFixed(2)}%`;
}

function formatSeconds(value) {
  const normalized = Number(value || 0);
  return `${normalized.toFixed(1)} c`;
}

function anomalyStatusLabel(status) {
  const map = {
    anomaly: "резкое изменение",
    growth: "рост",
    decline: "снижение",
    stable: "стабильно",
    insufficient: "недостаточно данных",
  };
  return map[status] || "статус не определён";
}

function anomalyStatusClass(status) {
  return `status-${status || "unknown"}`;
}

function aiPriorityLabel(priority) {
  const normalized = String(priority || "").trim().toLowerCase();
  if (normalized === "high") return "Высокий";
  if (normalized === "low") return "Низкий";
  return "Средний";
}

function setActiveBehaviorTab(tabId) {
  const key = String(tabId || "").trim();
  if (!key) return;
  activeBehaviorTab.value = key;
}

async function refreshAiRecommendations() {
  await loadAiRecommendations({ force: true });
}

async function manualRefresh() {
  await Promise.all([loadSummary(), loadAiRecommendations()]);
}

defineExpose({ manualRefresh });

onMounted(manualRefresh);
</script>

<style scoped>
.behavior-stats {
  grid-template-columns: repeat(auto-fit, minmax(12.5rem, 1fr));
}

.loading-note {
  margin-top: 0.75rem;
}

.card-head-wrap {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.behavior-ai-card {
  margin-top: 0.75rem;
}

.ai-refresh-btn {
  min-height: 2.25rem;
  border-radius: 0.65rem;
  border: 1px solid #bfdbfe;
  background: #eff6ff;
  color: #1e40af;
  padding: 0 0.85rem;
  font-weight: 600;
  cursor: pointer;
}

.ai-refresh-btn:disabled {
  opacity: 0.65;
  cursor: default;
}

.ai-summary {
  margin: 0 0 0.55rem;
}

.ai-meta {
  display: flex;
  gap: 0.65rem;
  flex-wrap: wrap;
  margin-bottom: 0.55rem;
}

.ai-meta .status-badge {
  text-transform: none;
}

.ai-items {
  margin: 0;
  padding-left: 1rem;
  display: grid;
  gap: 0.35rem;
}

.block-help {
  margin: 0 0 0.7rem;
}

.scroll-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(12rem, 1fr));
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.scroll-metric {
  border: 1px solid #d9e2ec;
  border-radius: 0.75rem;
  padding: 0.75rem;
  display: grid;
  gap: 0.25rem;
  background: #f8fafc;
}

.thresholds-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(11rem, 1fr));
  gap: 0.7rem;
}

.threshold-item {
  border: 1px solid #d9e2ec;
  border-radius: 0.75rem;
  padding: 0.75rem;
  background: #f8fafc;
  display: grid;
  gap: 0.25rem;
}

.threshold-title {
  font-weight: 600;
}

.threshold-help {
  font-size: 0.75rem;
}

.field-highlights {
  display: grid;
  gap: 0.35rem;
  margin-bottom: 0.75rem;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  min-height: 1.45rem;
  padding: 0 0.55rem;
  border-radius: 999px;
  font-size: 0.74rem;
  font-weight: 600;
  text-transform: lowercase;
  border: 1px solid transparent;
}

.status-anomaly {
  color: #b91c1c;
  background: #fee2e2;
  border-color: #fecaca;
}

.status-growth {
  color: #166534;
  background: #dcfce7;
  border-color: #bbf7d0;
}

.status-decline {
  color: #9a3412;
  background: #ffedd5;
  border-color: #fed7aa;
}

.status-stable {
  color: #1d4ed8;
  background: #dbeafe;
  border-color: #bfdbfe;
}

.status-insufficient,
.status-unknown {
  color: #374151;
  background: #f3f4f6;
  border-color: #d1d5db;
}

.status-priority-high {
  color: #991b1b;
  background: #fee2e2;
  border-color: #fecaca;
}

.status-priority-medium {
  color: #92400e;
  background: #fef3c7;
  border-color: #fde68a;
}

.status-priority-low {
  color: #166534;
  background: #dcfce7;
  border-color: #bbf7d0;
}

.compact-note {
  margin-bottom: 1rem;
}
</style>
