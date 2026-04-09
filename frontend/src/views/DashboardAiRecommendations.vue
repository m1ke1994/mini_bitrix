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
          <span v-if="aiRecommendationsLoading" class="ai-spinner ai-spinner-inline" aria-hidden="true"></span>
          {{ aiRecommendationsLoading ? "Обновление..." : "Обновить рекомендации" }}
        </button>
      </div>
      <p class="muted block-help">
        Короткая сводка по точкам роста: как упростить путь пользователя и повысить число заявок.
      </p>
      <div v-if="behaviorAiMode === 'loading'" class="ai-state ai-state-loading">
        <span class="ai-spinner" aria-hidden="true"></span>
        <p class="muted">Готовим рекомендации по поведенческим данным...</p>
      </div>
      <template v-else-if="behaviorAiMode === 'ai-success' || behaviorAiMode === 'fallback'">
        <p class="ai-summary">{{ behaviorAiSummary }}</p>
        <div class="ai-meta ai-meta-spaced">
          <span class="status-badge" :class="`status-priority-${behaviorAiPriority}`">
            Приоритет: {{ aiPriorityLabel(behaviorAiPriority) }}
          </span>
          <span class="muted">Источник: {{ behaviorAiSourceLabel }}</span>
          <span v-if="aiRecommendations.cached && behaviorAiMode === 'ai-success'" class="muted">
            Кэшированный ответ
          </span>
        </div>

        <div v-if="behaviorAiMode === 'fallback'" class="ai-fallback-banner" role="status" aria-live="polite">
          {{ behaviorAiFallbackMessage }}
        </div>

        <ul v-if="behaviorAiItems.length" class="ai-items">
          <li v-for="(item, idx) in behaviorAiItems" :key="`behavior-ai-item-${idx}`">{{ item }}</li>
        </ul>
        <p v-else class="muted">Пока нет готовых рекомендаций. Попробуйте обновить позже.</p>
      </template>
      <div v-else-if="behaviorAiMode === 'empty-data'" class="ai-state ai-state-empty">
        <p class="muted">
          Недостаточно данных для точных рекомендаций. Соберите больше визитов и взаимодействий.
        </p>
      </div>
      <div v-else class="ai-state ai-state-error">
        <p class="muted">{{ behaviorAiErrorMessage }}</p>
      </div>
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

const BEHAVIOR_RECOMMENDATIONS_MAX = 6;
const BEHAVIOR_RECOMMENDATIONS_MIN = 3;
const BEHAVIOR_MIN_USERS_FOR_RECOMMENDATIONS = 12;
const BEHAVIOR_MIN_VISITS_FOR_RECOMMENDATIONS = 30;

const internalBehaviorPathPatterns = [
  /^\/app\/dashboard/i,
  /^\/api(\/|$)/i,
  /^\/admin(\/|$)/i,
  /^\/auth(\/|$)/i,
  /^\/login(\/|$)/i,
  /^\/register(\/|$)/i,
];

const blockedBehaviorRecommendationKeywords = [
  "seo",
  "индексац",
  "meta",
  "title",
  "description",
  "canonical",
  "robots",
  "sitemap",
  "h1",
  "ttfb",
];

const behaviorPageRows = computed(() =>
  normalizeBehaviorPageRows(summary.value.conversion_by_pages, summary.value.engagement_pages)
);

const behaviorTotalVisits = computed(() =>
  behaviorPageRows.value.reduce((sum, row) => sum + Number(row.visits || 0), 0)
);

const hasEnoughDataForRecommendations = computed(() => {
  if (uniqueUsersInAnalysis.value >= BEHAVIOR_MIN_USERS_FOR_RECOMMENDATIONS) return true;
  if (behaviorTotalVisits.value >= BEHAVIOR_MIN_VISITS_FOR_RECOMMENDATIONS) return true;
  if (formStartedCount.value >= 6) return true;
  if (formSubmitSuccessCount.value >= 2) return true;
  return false;
});

const localBehaviorFallbackRecommendations = computed(() =>
  buildBehaviorFallbackRecommendations({
    pages: behaviorPageRows.value,
    totalVisits: behaviorTotalVisits.value,
    uniqueUsers: uniqueUsersInAnalysis.value,
    avgScrollDepth: avgScrollDepthValue.value,
    formVisible: formVisibleCount.value,
    formStarted: formStartedCount.value,
    formSubmitAttempt: formSubmitAttemptCount.value,
    formSubmitSuccess: formSubmitSuccessCount.value,
    formSubmitError: formSubmitErrorCount.value,
    ctaRows: ctaRows.value,
    hasEnoughData: hasEnoughDataForRecommendations.value,
  })
);

const aiNormalizedItems = computed(() => normalizeBehaviorAiItems(aiRecommendations.value));
const aiSource = computed(() => String(aiRecommendations.value?.source || "").trim().toLowerCase());
const aiFallbackFlag = computed(
  () => normalizeBooleanFlag(aiRecommendations.value?.fallback, aiSource.value === "fallback") || aiSource.value === "fallback"
);
const aiSuccessFlag = computed(() =>
  normalizeBooleanFlag(aiRecommendations.value?.success, aiSource.value === "ai" || aiSource.value === "openai")
);

const aiHasUsableRecommendations = computed(() => aiNormalizedItems.value.length > 0);
const aiResponseLooksSuccessful = computed(() => {
  if (aiFallbackFlag.value) return false;
  if (aiSource.value === "ai" || aiSource.value === "openai") return aiHasUsableRecommendations.value || aiSuccessFlag.value;
  return aiSuccessFlag.value && aiHasUsableRecommendations.value;
});

const behaviorAiMode = computed(() => {
  if (loading.value || aiRecommendationsLoading.value) return "loading";
  if (aiResponseLooksSuccessful.value && aiHasUsableRecommendations.value) return "ai-success";
  if (localBehaviorFallbackRecommendations.value.length) return "fallback";
  if (!hasEnoughDataForRecommendations.value) return "empty-data";
  if (aiRecommendationsError.value) return "error";
  return "empty-data";
});

const behaviorAiItems = computed(() => {
  if (behaviorAiMode.value === "ai-success") return aiNormalizedItems.value.slice(0, BEHAVIOR_RECOMMENDATIONS_MAX);
  if (behaviorAiMode.value === "fallback") {
    return localBehaviorFallbackRecommendations.value.slice(0, BEHAVIOR_RECOMMENDATIONS_MAX);
  }
  return [];
});

const behaviorAiPriority = computed(() => {
  if (behaviorAiMode.value !== "ai-success") return "medium";
  const normalized = String(aiRecommendations.value?.priority || "").trim().toLowerCase();
  if (normalized === "high" || normalized === "medium" || normalized === "low") return normalized;
  return "medium";
});

const behaviorAiSummary = computed(() => {
  if (behaviorAiMode.value === "ai-success") {
    const fromAi = sanitizeBehaviorRecommendationText(aiRecommendations.value?.summary, 220);
    if (fromAi) return fromAi;
    return "AI выделил ключевые поведенческие точки роста для повышения конверсии.";
  }
  if (behaviorAiMode.value === "fallback") {
    return "Локальные рекомендации собраны по фактическим метрикам поведения пользователей.";
  }
  if (behaviorAiMode.value === "empty-data") {
    return "Недостаточно данных для точных рекомендаций.";
  }
  return "Не удалось получить рекомендации по поведенческим данным.";
});

const behaviorAiSourceLabel = computed(() => {
  if (behaviorAiMode.value === "ai-success") return "AI";
  if (behaviorAiMode.value === "fallback") return "локальный анализ";
  return "не определён";
});

const behaviorAiFallbackMessage = computed(() => {
  const requestError = sanitizeBehaviorRecommendationText(aiRecommendationsError.value, 220);
  if (requestError) return `AI временно недоступен: ${requestError}`;
  const payloadMessage = sanitizeBehaviorRecommendationText(aiRecommendations.value?.user_message, 220);
  if (payloadMessage) return payloadMessage;
  return "AI не вернул пригодный ответ. Показаны fallback-рекомендации по текущей аналитике.";
});

const behaviorAiErrorMessage = computed(() => {
  const requestError = sanitizeBehaviorRecommendationText(aiRecommendationsError.value, 220);
  if (requestError) return requestError;
  return "Не удалось загрузить рекомендации. Попробуйте обновить данные позже.";
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

function normalizeBooleanFlag(value, defaultValue = false) {
  if (typeof value === "boolean") return value;
  if (typeof value === "number") return value !== 0;
  if (typeof value === "string") {
    const normalized = value.trim().toLowerCase();
    if (["1", "true", "yes", "ok", "success"].includes(normalized)) return true;
    if (["0", "false", "no", "none", "null", ""].includes(normalized)) return false;
  }
  return defaultValue;
}

function sanitizeBehaviorRecommendationText(value, maxLen = 220) {
  let text = String(value || "").trim();
  if (!text) return "";
  text = text
    .replace(/[`_*#]+/g, " ")
    .replace(/\r?\n+/g, " ")
    .replace(/^\s*[-*+\d.)\]]+\s*/g, "")
    .replace(/\s{2,}/g, " ")
    .trim();
  if (!text) return "";
  if (text.length > maxLen) {
    return `${text.slice(0, maxLen - 3).trim()}...`;
  }
  return text;
}

function normalizePathname(value) {
  const raw = String(value || "").trim();
  if (!raw) return "";
  try {
    if (/^https?:\/\//i.test(raw)) {
      const parsed = new URL(raw);
      const path = String(parsed.pathname || "/").trim();
      return path || "/";
    }
  } catch {
    // ignore and keep raw
  }
  const [withoutQuery] = raw.split(/[?#]/);
  if (!withoutQuery) return "/";
  return withoutQuery.startsWith("/") ? withoutQuery : `/${withoutQuery}`;
}

function isInternalBehaviorPath(pathname) {
  const normalized = String(pathname || "").trim().toLowerCase();
  if (!normalized) return true;
  return internalBehaviorPathPatterns.some((pattern) => pattern.test(normalized));
}

function shortPathnameLabel(pathname) {
  const normalized = normalizePathname(pathname);
  if (!normalized) return "/";
  const clipped = normalized.length > 46 ? `${normalized.slice(0, 43)}...` : normalized;
  return clipped;
}

function normalizeBehaviorPageRows(conversionRows, engagementRows) {
  const resultMap = new Map();

  const readRows = (rows, type) => {
    if (!Array.isArray(rows)) return;
    for (const row of rows) {
      const pathname = normalizePathname(
        row?.pathname || row?.path || row?.url || row?.page_pathname || row?.page || ""
      );
      if (!pathname || isInternalBehaviorPath(pathname)) continue;

      const visits =
        Number(row?.visits || row?.visits_count || row?.sessions || row?.views || row?.count || 0) || 0;
      const leads = Number(row?.leads || row?.form_submit_success || row?.conversions || 0) || 0;
      const conversionPctRaw = Number(row?.conversion_pct || row?.conversion_rate_pct || 0) || 0;
      const conversionPct = conversionPctRaw > 0 ? conversionPctRaw : visits > 0 ? (leads / visits) * 100 : 0;

      const prev = resultMap.get(pathname) || { pathname, visits: 0, leads: 0, conversionPct: 0, source: type };
      const mergedVisits = Math.max(prev.visits, visits);
      const mergedLeads = Math.max(prev.leads, leads);
      const mergedConversion = mergedVisits > 0 ? (mergedLeads / mergedVisits) * 100 : Math.max(prev.conversionPct, conversionPct);

      resultMap.set(pathname, {
        pathname,
        visits: Math.round(mergedVisits),
        leads: Math.round(mergedLeads),
        conversionPct: Number(mergedConversion.toFixed(2)),
        source: prev.source === "conversion" || type === "conversion" ? "conversion" : type,
      });
    }
  };

  readRows(conversionRows, "conversion");
  readRows(engagementRows, "engagement");

  return [...resultMap.values()]
    .filter((row) => row.visits > 0)
    .sort((left, right) => right.visits - left.visits);
}

function formatPathList(rows, maxItems = 2) {
  return rows
    .slice(0, maxItems)
    .map((row) => `"${shortPathnameLabel(row.pathname)}"`)
    .join(", ");
}

function isBehaviorRecommendationAllowed(text) {
  const normalized = String(text || "").trim().toLowerCase();
  if (!normalized) return false;
  if (normalized.includes("```") || normalized.includes("json") || normalized.includes("prompt")) return false;
  return !blockedBehaviorRecommendationKeywords.some((keyword) => normalized.includes(keyword));
}

function normalizeBehaviorAiItems(payload) {
  if (!payload || typeof payload !== "object") return [];
  const result = [];
  const seen = new Set();

  const pushItem = (value) => {
    const cleaned = sanitizeBehaviorRecommendationText(value, 240);
    if (!cleaned || !isBehaviorRecommendationAllowed(cleaned)) return;
    const dedupeKey = cleaned.toLowerCase();
    if (seen.has(dedupeKey)) return;
    seen.add(dedupeKey);
    result.push(cleaned);
  };

  if (Array.isArray(payload.items)) {
    payload.items.forEach((item) => pushItem(item));
  }

  if (Array.isArray(payload.recommendations)) {
    payload.recommendations.forEach((item) => {
      if (typeof item === "string") {
        pushItem(item);
        return;
      }
      const problem = sanitizeBehaviorRecommendationText(item?.problem || item?.title || "", 130);
      const fix = sanitizeBehaviorRecommendationText(item?.fix || item?.details || item?.recommendation || "", 210);
      if (problem && fix) {
        pushItem(`${problem}: ${fix}`);
      } else if (fix) {
        pushItem(fix);
      } else if (problem) {
        pushItem(problem);
      }
    });
  }

  if (!result.length && typeof payload.text === "string") {
    payload.text
      .split(/\r?\n/)
      .map((line) => sanitizeBehaviorRecommendationText(line, 240))
      .filter((line) => line.length > 12)
      .forEach((line) => pushItem(line));
  }

  return result.slice(0, BEHAVIOR_RECOMMENDATIONS_MAX);
}

function buildBehaviorFallbackRecommendations({
  pages,
  totalVisits,
  uniqueUsers,
  avgScrollDepth,
  formVisible,
  formStarted,
  formSubmitAttempt,
  formSubmitSuccess,
  formSubmitError,
  ctaRows,
  hasEnoughData,
}) {
  if (!hasEnoughData) return [];

  const recommendations = [];
  const usedKeys = new Set();
  const pushRecommendation = (key, text) => {
    if (usedKeys.has(key)) return;
    const cleaned = sanitizeBehaviorRecommendationText(text, 260);
    if (!cleaned) return;
    usedKeys.add(key);
    recommendations.push(cleaned);
  };

  const highTrafficThreshold = Math.max(20, Math.round(totalVisits * 0.12));
  const highTrafficPages = pages.filter((row) => row.visits >= highTrafficThreshold);
  const zeroLeadPages = highTrafficPages.filter((row) => row.leads === 0);
  const lowConversionPages = highTrafficPages.filter(
    (row) => row.visits >= highTrafficThreshold && row.conversionPct < 1 && row.leads <= 1
  );
  const bestConvertingPage = [...pages]
    .filter((row) => row.visits >= 10 && row.leads >= 2 && row.conversionPct > 0)
    .sort((left, right) => right.conversionPct - left.conversionPct)[0];

  if (zeroLeadPages.length) {
    pushRecommendation(
      "zero-lead-pages",
      `На страницах ${formatPathList(zeroLeadPages)} есть трафик без заявок. Усильте оффер первого экрана и добавьте заметный CTA рядом с ключевым контентом.`
    );
  }

  if (lowConversionPages.length) {
    pushRecommendation(
      "low-conversion-pages",
      `На страницах ${formatPathList(lowConversionPages)} много визитов и слабая конверсия. Проверьте понятность следующего шага и уберите лишние действия до заявки.`
    );
  }

  if (formVisible > 0) {
    const formStartRate = (formStarted / formVisible) * 100;
    if (formStartRate < 22) {
      pushRecommendation(
        "form-visibility",
        "Переход к началу формы слабый. Сделайте кнопку и форму заметнее в первом экране и добавьте короткий оффер рядом с CTA."
      );
    }
  }

  if (formStarted > 0) {
    const formCompletionRate = (formSubmitSuccess / formStarted) * 100;
    if (formCompletionRate < 45) {
      pushRecommendation(
        "form-completion",
        "Пользователи начинают, но не завершают форму. Сократите количество полей, уберите лишние шаги и оставьте только критично важные данные."
      );
    }
  }

  if (formSubmitAttempt > 0) {
    const formErrorRate = (formSubmitError / formSubmitAttempt) * 100;
    if (formErrorRate >= 12) {
      pushRecommendation(
        "form-errors",
        "Доля ошибок при отправке формы заметная. Проверьте валидацию полей и тексты ошибок, чтобы пользователь понимал, как быстро исправить ввод."
      );
    }
  }

  if (avgScrollDepth > 0 && avgScrollDepth < 45 && uniqueUsers >= BEHAVIOR_MIN_USERS_FOR_RECOMMENDATIONS) {
    pushRecommendation(
      "low-scroll-depth",
      "Глубина просмотра ниже ожидаемой. Упростите структуру ключевых страниц, добавьте более явные подзаголовки и CTA в верхней части контента."
    );
  }

  if (bestConvertingPage && (zeroLeadPages.length || lowConversionPages.length)) {
    pushRecommendation(
      "best-page-pattern",
      `Страница ${shortPathnameLabel(bestConvertingPage.pathname)} конвертирует лучше других. Перенесите её паттерны оффера и CTA на слабые страницы с высоким трафиком.`
    );
  }

  const weakCta = Array.isArray(ctaRows)
    ? ctaRows.find((row) => {
        const shows = Number(row?.shows || 0);
        const ctr = Number(row?.ctr_pct || 0);
        return shows >= 40 && ctr > 0 && ctr < 1.2;
      })
    : null;
  if (weakCta) {
    pushRecommendation(
      "weak-cta",
      "На части кнопок низкий CTR. Перепроверьте текст CTA: добавьте конкретную пользу и действие, которое пользователь получит сразу после клика."
    );
  }

  if (recommendations.length < BEHAVIOR_RECOMMENDATIONS_MIN) {
    pushRecommendation(
      "primary-cta-focus",
      "На ключевых страницах оставьте один главный сценарий до заявки: один основной CTA, короткий оффер и минимум отвлекающих блоков."
    );
  }
  if (recommendations.length < BEHAVIOR_RECOMMENDATIONS_MIN) {
    pushRecommendation(
      "trust-near-form",
      "Добавьте рядом с формой блоки доверия: кейсы, гарантии, сроки ответа и быстрый способ связи для сомневающихся пользователей."
    );
  }
  if (recommendations.length < BEHAVIOR_RECOMMENDATIONS_MIN) {
    pushRecommendation(
      "measure-form-steps",
      "Проверьте шаги до заявки по этапам воронки и закрепите целевой ориентир: рост перехода от начала формы к успешной отправке."
    );
  }

  return recommendations.slice(0, BEHAVIOR_RECOMMENDATIONS_MAX);
}

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
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
  cursor: pointer;
}

.ai-refresh-btn:disabled {
  opacity: 0.65;
  cursor: default;
}

.ai-spinner {
  width: 0.92rem;
  height: 0.92rem;
  border-radius: 999px;
  border: 2px solid #bfdbfe;
  border-top-color: #2563eb;
  animation: behavior-ai-spin 0.9s linear infinite;
  flex-shrink: 0;
}

.ai-spinner-inline {
  width: 0.82rem;
  height: 0.82rem;
}

.ai-state {
  border: 1px solid #dbeafe;
  border-radius: 0.8rem;
  background: #f8fbff;
  padding: 0.72rem 0.8rem;
}

.ai-state-loading {
  display: inline-flex;
  align-items: center;
  gap: 0.52rem;
}

.ai-state-loading p {
  margin: 0;
}

.ai-state-empty,
.ai-state-error {
  display: block;
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

.ai-meta-spaced {
  margin-bottom: 0.5rem;
}

.ai-meta .status-badge {
  text-transform: none;
}

.ai-fallback-banner {
  margin-bottom: 0.58rem;
  padding: 0.58rem 0.68rem;
  border-radius: 0.72rem;
  border: 1px solid #fde68a;
  background: #fffbeb;
  color: #92400e;
  font-size: 0.84rem;
  line-height: 1.45;
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

@keyframes behavior-ai-spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
