<template>
  <section class="dashboard-section seo-audit-page">
    <p v-if="error" class="error">{{ error }}</p>

    <div class="chart-card">
      <div class="card-head card-head-wrap">
        <h2>SEO-аудит сайта</h2>
        <button type="button" class="seo-export-btn" :disabled="!canExport" @click="exportReport">
          {{ exporting ? "Подготовка..." : "Экспортировать отчёт" }}
        </button>
      </div>

      <div class="seo-start-row">
        <label class="seo-field">
          <span class="seo-field-label">Домен</span>
          <input
            v-model.trim="domain"
            type="text"
            class="seo-input"
            placeholder="example.com"
            autocomplete="off"
          />
        </label>
        <button
          type="button"
          class="seo-start-btn"
          :class="{ 'is-busy': isInProgress }"
          :disabled="!canStartAudit"
          @click="startAudit"
        >
          {{ starting ? "Запуск..." : "Запустить аудит" }}
        </button>
        <button type="button" class="seo-stop-btn" :disabled="!canStopAudit" @click="stopAudit">
          {{ stopping ? "Остановка..." : "Остановить аудит" }}
        </button>
      </div>

      <p v-if="isInProgress" class="seo-running-indicator" role="status" aria-live="polite">
        <span class="seo-spinner" aria-hidden="true"></span>
        {{ runningHint }}
      </p>

      <p class="muted seo-hint">
        Введите домен сайта. Аудит показывает технические проблемы и готовность страниц к заявкам.
      </p>
    </div>

    <div class="stats seo-stats">
      <article class="stat-card">
        <h3>Статус</h3>
        <strong :class="statusClass">{{ statusLabel }}</strong>
      </article>
      <article class="stat-card">
        <h3>SEO-оценка</h3>
        <strong :class="scoreClass">{{ scoreValue }}</strong>
      </article>
      <article class="stat-card">
        <h3>Страниц проверено</h3>
        <strong>{{ audit?.pages_count ?? 0 }}</strong>
      </article>
      <article class="stat-card">
        <h3>Всего ошибок</h3>
        <strong>{{ errorsCount }}</strong>
      </article>
      <article class="stat-card">
        <h3>Средний отклик</h3>
        <strong>{{ formatMs(avgTtfbMs) }}</strong>
      </article>
      <article class="stat-card">
        <h3>Средняя скорость</h3>
        <strong :class="scoreClassByValue(avgPerformanceScore)">{{ avgPerformanceScore }}</strong>
      </article>
      <article class="stat-card">
        <h3>robots.txt</h3>
        <strong :class="hasRobotsTxt ? 'status-done' : 'status-error'">
          {{ hasRobotsTxt ? "Найден" : "Не найден" }}
        </strong>
      </article>
      <article class="stat-card">
        <h3>sitemap.xml</h3>
        <strong :class="hasSitemapXml ? 'status-done' : 'status-error'">
          {{ hasSitemapXml ? "Найден" : "Не найден" }}
        </strong>
      </article>
      <article class="stat-card">
        <h3>Проблемы скорости</h3>
        <strong>{{ pagesWithSpeedIssues }}</strong>
      </article>
      <article class="stat-card">
        <h3>Проблемы индексации</h3>
        <strong>{{ pagesWithIndexingIssues }}</strong>
      </article>
    </div>

    <div v-if="auditId" class="chart-card">
      <div class="card-head">
        <h2>Разбивка ошибок</h2>
      </div>
      <div class="seo-breakdown-grid">
        <article class="seo-breakdown-card seo-breakdown-high">
          <span>Критичные</span>
          <strong>{{ breakdown.high_issues }}</strong>
        </article>
        <article class="seo-breakdown-card seo-breakdown-medium">
          <span>Средние</span>
          <strong>{{ breakdown.medium_issues }}</strong>
        </article>
        <article class="seo-breakdown-card seo-breakdown-low">
          <span>Низкие</span>
          <strong>{{ breakdown.low_issues }}</strong>
        </article>
      </div>
    </div>

    <div v-if="auditId" class="chart-card">
      <div class="card-head">
        <h2>План исправлений: что чинить первым</h2>
      </div>
      <p class="muted block-hint">
        Начните с верхних задач: они дают самый быстрый эффект для SEO и заявок.
      </p>
      <div v-if="fixPlan.length" class="fix-plan-list">
        <article v-for="(item, index) in fixPlan" :key="`${item.title}-${index}`" class="fix-plan-item">
          <div class="fix-plan-head">
            <strong>{{ item.title }}</strong>
            <span class="priority-pill" :class="priorityClass(item.priority_key)">{{ item.priority_label }}</span>
          </div>
          <p class="muted">{{ item.why_it_matters }}</p>
          <div class="fix-plan-meta">
            <span>Затронуто страниц: <strong>{{ item.pages_affected }}</strong></span>
            <span>Где смотреть: <strong>{{ item.target_block }}</strong></span>
          </div>
        </article>
      </div>
      <p v-else class="muted empty-state">Пока нет заметных проблем. Запустите аудит после обновлений на сайте.</p>
    </div>

    <div v-if="auditId" class="chart-card">
      <div class="card-head card-head-wrap">
        <h2>Группировка проблем по типам</h2>
        <button type="button" class="collapse-btn" @click="toggleBlock('issueGroups')">
          {{ collapsed.issueGroups ? "Развернуть" : "Свернуть" }}
        </button>
      </div>
      <p class="muted block-hint">
        Блок помогает понять, какие ошибки лучше исправлять пакетно.
      </p>

      <template v-if="!collapsed.issueGroups">
        <div v-if="issueGroups.length" class="table-wrap">
          <table class="table">
            <thead>
              <tr>
                <th>Тип проблемы</th>
                <th>Страниц</th>
                <th>Уровень</th>
                <th>Почему важно</th>
                <th>Действие</th>
              </tr>
            </thead>
            <tbody>
              <template v-for="group in issueGroups" :key="group.issue_type">
                <tr>
                  <td>{{ group.title }}</td>
                  <td>{{ group.pages_affected }}</td>
                  <td>
                    <span class="severity-pill" :class="`severity-${group.severity}`">
                      {{ severityLabel(group.severity) }}
                    </span>
                  </td>
                  <td>{{ group.description }}</td>
                  <td>
                    <button
                      type="button"
                      class="issue-pages-toggle"
                      :disabled="!group.pages_affected"
                      @click="toggleIssueGroupPages(group.issue_type)"
                    >
                      {{ isIssueGroupExpanded(group.issue_type) ? "Скрыть страницы" : `Показать страницы (${group.pages_affected})` }}
                    </button>
                  </td>
                </tr>
                <tr v-if="isIssueGroupExpanded(group.issue_type)">
                  <td colspan="5">
                    <div v-if="group.pages?.length" class="issue-pages-list">
                      <span v-for="pageUrl in group.pages" :key="`${group.issue_type}-${pageUrl}`">{{ pageUrl }}</span>
                    </div>
                    <p v-else class="muted">Список страниц для этого типа пока не сформирован.</p>
                  </td>
                </tr>
              </template>
            </tbody>
          </table>
        </div>
        <p v-else class="muted empty-state">Проблемы по типам пока не обнаружены.</p>
      </template>
    </div>

    <div v-if="auditId" class="chart-card">
      <div class="card-head card-head-wrap">
        <h2>Сравнение аудитов во времени</h2>
        <button type="button" class="seo-compare-btn" :disabled="!canCompare || comparisonLoading" @click="compareAudits">
          {{ comparisonLoading ? "Сравнение..." : "Сравнить аудит" }}
        </button>
      </div>
      <p class="muted block-hint">
        Сравнение показывает прогресс: что исправлено, что ухудшилось и как изменился сайт.
      </p>

      <div v-if="historyRows.length" class="compare-controls">
        <label class="seo-field">
          <span class="seo-field-label">Сравнить с аудитом</span>
          <select v-model="selectedCompareAuditId" class="seo-select">
            <option v-for="item in historyRows" :key="`history-${item.audit_id}`" :value="String(item.audit_id)">
              #{{ item.audit_id }} · {{ formatDate(item.created_at) }} · SEO {{ item.score }}
            </option>
          </select>
        </label>
      </div>

      <div v-if="comparisonPayload?.has_data" class="comparison-wrap">
        <p class="comparison-trend" :class="comparisonTrendClass(comparisonPayload?.trend)">
          {{ comparisonPayload?.trend_label }}
        </p>
        <div class="comparison-grid">
          <article class="comparison-card">
            <span>SEO-оценка</span>
            <strong>{{ comparisonPayload.score.before }} → {{ comparisonPayload.score.after }}</strong>
            <small>{{ signedDelta(comparisonPayload.score.delta) }}</small>
          </article>
          <article class="comparison-card">
            <span>Критичные ошибки</span>
            <strong>{{ comparisonPayload.issues.high.before }} → {{ comparisonPayload.issues.high.after }}</strong>
            <small>{{ signedDelta(comparisonPayload.issues.high.delta) }}</small>
          </article>
          <article class="comparison-card">
            <span>Средние ошибки</span>
            <strong>{{ comparisonPayload.issues.medium.before }} → {{ comparisonPayload.issues.medium.after }}</strong>
            <small>{{ signedDelta(comparisonPayload.issues.medium.delta) }}</small>
          </article>
          <article class="comparison-card">
            <span>Низкие ошибки</span>
            <strong>{{ comparisonPayload.issues.low.before }} → {{ comparisonPayload.issues.low.after }}</strong>
            <small>{{ signedDelta(comparisonPayload.issues.low.delta) }}</small>
          </article>
          <article class="comparison-card">
            <span>Проблемы скорости</span>
            <strong>{{ comparisonPayload.speed_pages.before }} → {{ comparisonPayload.speed_pages.after }}</strong>
            <small>{{ signedDelta(comparisonPayload.speed_pages.delta) }}</small>
          </article>
          <article class="comparison-card">
            <span>Проблемы индексации</span>
            <strong>{{ comparisonPayload.indexing_pages.before }} → {{ comparisonPayload.indexing_pages.after }}</strong>
            <small>{{ signedDelta(comparisonPayload.indexing_pages.delta) }}</small>
          </article>
        </div>

        <div class="comparison-index-files">
          <article>
            <span class="muted">robots.txt:</span>
            <strong>{{ boolTransitionLabel(comparisonPayload.robots_txt.status) }}</strong>
          </article>
          <article>
            <span class="muted">sitemap.xml:</span>
            <strong>{{ boolTransitionLabel(comparisonPayload.sitemap_xml.status) }}</strong>
          </article>
        </div>

        <div class="comparison-lists">
          <article>
            <h3>Новые проблемы</h3>
            <p class="muted small">{{ comparisonPayload.new_issues_count }} шт.</p>
            <ul v-if="comparisonPayload.new_issues?.length" class="comparison-issue-list">
              <li v-for="item in comparisonPayload.new_issues" :key="`new-${item.issue_type}-${item.page_url}`">
                {{ item.issue_title }} — {{ item.page_url }}
              </li>
            </ul>
            <p v-else class="muted">Новых проблем не найдено.</p>
          </article>
          <article>
            <h3>Исправленные проблемы</h3>
            <p class="muted small">{{ comparisonPayload.fixed_issues_count }} шт.</p>
            <ul v-if="comparisonPayload.fixed_issues?.length" class="comparison-issue-list">
              <li v-for="item in comparisonPayload.fixed_issues" :key="`fixed-${item.issue_type}-${item.page_url}`">
                {{ item.issue_title }} — {{ item.page_url }}
              </li>
            </ul>
            <p v-else class="muted">Исправленных проблем пока нет.</p>
          </article>
        </div>
      </div>
      <p v-else class="muted empty-state">{{ comparisonPayload?.reason || "Для сравнения нужен завершённый аудит." }}</p>
    </div>

    <div v-if="auditId" class="chart-card">
      <div class="card-head card-head-wrap">
        <h2>Коммерческий SEO-аудит страницы</h2>
        <button type="button" class="collapse-btn" @click="toggleBlock('commercial')">
          {{ collapsed.commercial ? "Развернуть" : "Свернуть" }}
        </button>
      </div>
      <p class="muted block-hint">
        Проверка показывает, насколько страницы готовы к заявкам: форма, CTA, контакты, оффер, преимущества, FAQ.
      </p>

      <template v-if="!collapsed.commercial">
        <div v-if="commercialSummary.has_data" class="commercial-summary-grid">
          <article class="commercial-summary-card">
            <span>Средняя готовность</span>
            <strong :class="scoreClassByValue(commercialSummary.avg_score)">{{ commercialSummary.avg_score }}/100</strong>
          </article>
          <article class="commercial-summary-card">
            <span>Готовы к заявкам</span>
            <strong class="status-done">{{ commercialSummary.good_pages }}</strong>
          </article>
          <article class="commercial-summary-card">
            <span>Есть замечания</span>
            <strong class="status-stopped">{{ commercialSummary.warning_pages }}</strong>
          </article>
          <article class="commercial-summary-card">
            <span>Слабо подготовлены</span>
            <strong class="status-error">{{ commercialSummary.critical_pages }}</strong>
          </article>
        </div>

        <div v-if="commercialSummary.top_recommendations?.length" class="recommendation-list">
          <h3>Что улучшить в первую очередь</h3>
          <ul>
            <li v-for="item in commercialSummary.top_recommendations" :key="item.text">
              {{ item.text }} <span class="muted">(затронуто: {{ item.pages_affected }})</span>
            </li>
          </ul>
        </div>

        <div class="table-wrap">
          <table class="table">
            <thead>
              <tr>
                <th>URL</th>
                <th>Статус</th>
                <th>Оценка</th>
                <th>Сигналы</th>
                <th>Рекомендации</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="page in commercialPages" :key="`commercial-${page.id}`">
                <td class="url-cell">{{ page.url }}</td>
                <td>
                  <span class="severity-pill" :class="commercialStatusClass(page.commercial_status)">
                    {{ page.commercial_status_label || commercialStatusLabel(page.commercial_status) }}
                  </span>
                </td>
                <td>{{ page.commercial_readiness_score ?? 0 }}/100</td>
                <td>
                  <div class="signal-grid">
                    <span :class="signalClass(page.commercial_signals?.has_form)">Форма</span>
                    <span :class="signalClass(page.commercial_signals?.has_cta)">CTA</span>
                    <span :class="signalClass(page.commercial_signals?.has_phone_or_contact)">Контакт</span>
                    <span :class="signalClass(page.commercial_signals?.has_messenger)">Мессенджер</span>
                    <span :class="signalClass(page.commercial_signals?.has_offer_like_heading)">Оффер</span>
                    <span :class="signalClass(page.commercial_signals?.has_benefits_block)">Преимущества</span>
                    <span :class="signalClass(page.commercial_signals?.has_faq)">FAQ</span>
                  </div>
                </td>
                <td>
                  <ul v-if="page.commercial_recommendations?.length" class="recommendation-mini-list">
                    <li v-for="item in page.commercial_recommendations" :key="`${page.id}-${item}`">{{ item }}</li>
                  </ul>
                  <span v-else>Без замечаний</span>
                </td>
              </tr>
              <tr v-if="!commercialPages.length">
                <td colspan="5">Пока недостаточно данных для коммерческого анализа страниц.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
    </div>

    <div v-if="auditId" class="chart-card">
      <div class="card-head card-head-wrap">
        <h2>Скорость и производительность</h2>
        <button type="button" class="collapse-btn" @click="toggleBlock('speed')">
          {{ collapsed.speed ? "Развернуть" : "Свернуть" }}
        </button>
      </div>
      <p class="muted block-hint">Оценка построена по времени ответа, размеру страницы и объёму ресурсов.</p>

      <template v-if="!collapsed.speed">
        <div class="table-wrap">
          <table class="table">
            <thead>
              <tr>
                <th>URL</th>
                <th>TTFB</th>
                <th>HTML</th>
                <th>JS/CSS/IMG</th>
                <th>Вес JS/CSS/IMG</th>
                <th>Score</th>
                <th>Статус</th>
                <th>Проблемы</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="page in pages" :key="`speed-${page.id}`">
                <td class="url-cell">{{ page.url }}</td>
                <td>{{ formatMs(page.ttfb_ms) }}</td>
                <td>{{ formatBytes(page.html_size_bytes) }}</td>
                <td>{{ page.js_files_count || 0 }} / {{ page.css_files_count || 0 }} / {{ page.images_count || 0 }}</td>
                <td>
                  {{ formatBytes(page.total_js_bytes) }} /
                  {{ formatBytes(page.total_css_bytes) }} /
                  {{ formatBytes(page.total_image_bytes) }}
                </td>
                <td :class="scoreClassByValue(page.performance_score)">{{ page.performance_score ?? 0 }}</td>
                <td>
                  <span class="severity-pill" :class="speedStatusClass(page.speed_status)">
                    {{ speedStatusLabel(page.speed_status) }}
                  </span>
                </td>
                <td>
                  <span v-if="pageSpeedIssues(page).length" class="issue-inline-list">
                    {{ pageSpeedIssues(page).map(issueLabel).join(", ") }}
                  </span>
                  <span v-else>—</span>
                </td>
              </tr>
              <tr v-if="!pages.length">
                <td colspan="8">Пока недостаточно данных по скорости страниц.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
    </div>

    <div v-if="auditId" class="chart-card">
      <div class="card-head card-head-wrap">
        <h2>Индексация</h2>
        <button type="button" class="collapse-btn" @click="toggleBlock('indexing')">
          {{ collapsed.indexing ? "Развернуть" : "Свернуть" }}
        </button>
      </div>
      <p class="muted block-hint">Проверка показывает, как поисковые системы видят и обходят страницы.</p>
      <div class="indexing-summary">
        <div>
          <span class="muted">robots.txt:</span>
          <strong :class="hasRobotsTxt ? 'status-done' : 'status-error'">
            {{ hasRobotsTxt ? "доступен" : "не найден" }}
          </strong>
        </div>
        <div>
          <span class="muted">sitemap.xml:</span>
          <strong :class="hasSitemapXml ? 'status-done' : 'status-error'">
            {{ hasSitemapXml ? "доступен" : "не найден или некорректен" }}
          </strong>
        </div>
        <div>
          <span class="muted">URL в sitemap:</span>
          <strong>{{ audit?.sitemap_urls_count ?? 0 }}</strong>
        </div>
      </div>

      <template v-if="!collapsed.indexing">
        <div class="table-wrap">
          <table class="table">
            <thead>
              <tr>
                <th>URL</th>
                <th>Meta robots</th>
                <th>Canonical</th>
                <th>Индексация</th>
                <th>В sitemap</th>
                <th>Блок robots</th>
                <th>Проблемы</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="page in pages" :key="`indexing-${page.id}`">
                <td class="url-cell">{{ page.url }}</td>
                <td>{{ page.meta_robots || "—" }}</td>
                <td class="url-cell">{{ page.canonical_url || "—" }}</td>
                <td>
                  <span class="severity-pill" :class="indexabilityStatusClass(page.indexability_status)">
                    {{ indexabilityStatusLabel(page.indexability_status) }}
                  </span>
                </td>
                <td>{{ yesNo(page.in_sitemap) }}</td>
                <td>{{ yesNo(page.blocked_by_robots) }}</td>
                <td>
                  <span v-if="pageIndexingIssues(page).length" class="issue-inline-list">
                    {{ pageIndexingIssues(page).map(issueLabel).join(", ") }}
                  </span>
                  <span v-else>—</span>
                </td>
              </tr>
              <tr v-if="!pages.length">
                <td colspan="7">Пока недостаточно данных по индексации.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
    </div>

    <div v-if="auditId" class="chart-card">
      <div class="card-head card-head-wrap">
        <h2>Страницы</h2>
        <button type="button" class="collapse-btn" @click="toggleBlock('pages')">
          {{ collapsed.pages ? "Развернуть" : "Свернуть" }}
        </button>
      </div>
      <p class="muted block-hint">Базовая таблица по ключевым SEO-параметрам каждой страницы.</p>

      <template v-if="!collapsed.pages">
        <div class="table-wrap">
          <table class="table">
            <thead>
              <tr>
                <th>URL</th>
                <th>Код ответа</th>
                <th>Title</th>
                <th>Длина Title</th>
                <th>Длина Description</th>
                <th>H1</th>
                <th>Количество H1</th>
                <th>Слов</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="page in pages" :key="page.id">
                <td class="url-cell">{{ page.url }}</td>
                <td>{{ page.status_code }}</td>
                <td>{{ page.title || "—" }}</td>
                <td>{{ page.title_length }}</td>
                <td>{{ page.description_length }}</td>
                <td>{{ page.h1 || "—" }}</td>
                <td>{{ page.h1_count }}</td>
                <td>{{ page.word_count }}</td>
              </tr>
              <tr v-if="!pages.length">
                <td colspan="8">Пока нет данных по страницам.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
    </div>

    <div v-if="auditId" class="chart-card">
      <div class="card-head card-head-wrap">
        <h2>Ошибки</h2>
        <button type="button" class="collapse-btn" @click="toggleBlock('errors')">
          {{ collapsed.errors ? "Развернуть" : "Свернуть" }}
        </button>
      </div>
      <p class="muted block-hint">
        Подробный список ошибок по страницам. Используйте фильтр, чтобы быстро найти проблемные зоны.
      </p>

      <template v-if="!collapsed.errors">
        <div class="issue-filters">
          <button
            v-for="item in issueFilters"
            :key="item.value"
            type="button"
            class="issue-filter-btn"
            :class="{ active: issueFilter === item.value }"
            @click="issueFilter = item.value"
          >
            {{ item.label }}
          </button>
        </div>
        <div class="table-wrap">
          <table class="table">
            <thead>
              <tr>
                <th>Страница</th>
                <th>Тип</th>
                <th>Уровень</th>
                <th>Рекомендация</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="issue in filteredIssues" :key="issue.id">
                <td class="url-cell">{{ issue.page_url }}</td>
                <td>{{ issueLabel(issue) }}</td>
                <td>
                  <span class="severity-pill" :class="`severity-${issue.severity}`">
                    {{ severityLabel(issue.severity) }}
                  </span>
                </td>
                <td>{{ issue.recommendation }}</td>
              </tr>
              <tr v-if="!filteredIssues.length">
                <td colspan="4">Ошибок по выбранному фильтру не найдено.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
    </div>
  </section>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from "vue";

import api from "../services/api";

const STORAGE_AUDIT_ID_KEY = "tracknode:seo:lastAuditId";
const STORAGE_DOMAIN_KEY = "tracknode:seo:lastDomain";
const POLL_INTERVAL_MS = 5000;

const SPEED_ISSUE_TYPES = new Set([
  "slow_response",
  "large_page_size",
  "slow_ttfb",
  "large_html_size",
  "too_many_js",
  "too_many_css",
  "too_many_images",
  "heavy_js_payload",
  "heavy_css_payload",
  "heavy_images_payload",
  "heavy_page_payload",
]);

const INDEXING_ISSUE_TYPES = new Set([
  "missing_robots_txt",
  "robots_disallow_all",
  "robots_missing_sitemap",
  "missing_sitemap",
  "bad_sitemap_status",
  "sitemap_mismatch",
  "missing_canonical",
  "invalid_canonical",
  "canonical_conflict",
  "page_noindex",
  "page_nofollow",
  "blocked_by_robots",
  "sitemap_page_missing",
  "missing_meta_robots",
]);

const issueFilters = [
  { value: "all", label: "Все" },
  { value: "speed", label: "Скорость" },
  { value: "indexing", label: "Индексация" },
  { value: "other", label: "Прочее" },
];

const auditId = ref(null);
const audit = ref(null);
const domain = ref("");
const error = ref("");
const loading = ref(false);
const starting = ref(false);
const stopping = ref(false);
const exporting = ref(false);
const bootstrapping = ref(false);
const issueFilter = ref("all");

const historyRows = ref([]);
const selectedCompareAuditId = ref("");
const comparison = ref(null);
const comparisonLoading = ref(false);

const collapsed = ref({
  issueGroups: false,
  commercial: false,
  speed: true,
  indexing: true,
  pages: true,
  errors: true,
});
const expandedIssueGroups = ref({});

let pollTimer = null;

const pages = computed(() => (Array.isArray(audit.value?.pages) ? audit.value.pages : []));
const groupedErrors = computed(() => {
  const grouped = audit.value?.grouped_errors || {};
  return {
    high: Array.isArray(grouped.high) ? grouped.high : [],
    medium: Array.isArray(grouped.medium) ? grouped.medium : [],
    low: Array.isArray(grouped.low) ? grouped.low : [],
  };
});

const issues = computed(() => {
  if (Array.isArray(audit.value?.errors)) return audit.value.errors;
  return [...groupedErrors.value.high, ...groupedErrors.value.medium, ...groupedErrors.value.low];
});

const speedIssues = computed(() =>
  issues.value.filter((issue) => SPEED_ISSUE_TYPES.has(String(issue?.issue_type || "").toLowerCase())),
);
const indexingIssues = computed(() =>
  issues.value.filter((issue) => INDEXING_ISSUE_TYPES.has(String(issue?.issue_type || "").toLowerCase())),
);
const otherIssues = computed(() =>
  issues.value.filter((issue) => {
    const type = String(issue?.issue_type || "").toLowerCase();
    return !SPEED_ISSUE_TYPES.has(type) && !INDEXING_ISSUE_TYPES.has(type);
  }),
);

const filteredIssues = computed(() => {
  if (issueFilter.value === "speed") return speedIssues.value;
  if (issueFilter.value === "indexing") return indexingIssues.value;
  if (issueFilter.value === "other") return otherIssues.value;
  return issues.value;
});

const breakdown = computed(() => {
  const payload = audit.value?.breakdown;
  if (payload && typeof payload === "object") {
    return {
      score: Number(payload.score ?? audit.value?.score ?? 0) || 0,
      high_issues: Number(payload.high_issues ?? 0) || 0,
      medium_issues: Number(payload.medium_issues ?? 0) || 0,
      low_issues: Number(payload.low_issues ?? 0) || 0,
    };
  }
  return {
    score: Number(audit.value?.score ?? audit.value?.seo_score ?? 0) || 0,
    high_issues: groupedErrors.value.high.length,
    medium_issues: groupedErrors.value.medium.length,
    low_issues: groupedErrors.value.low.length,
  };
});

const fixPlan = computed(() => (Array.isArray(audit.value?.fix_plan) ? audit.value.fix_plan : []));
const issueGroups = computed(() => (Array.isArray(audit.value?.issue_groups) ? audit.value.issue_groups : []));
const commercialSummary = computed(() => {
  const payload = audit.value?.commercial_summary;
  if (payload && typeof payload === "object") return payload;
  return {
    has_data: false,
    pages_total: 0,
    avg_score: 0,
    good_pages: 0,
    warning_pages: 0,
    critical_pages: 0,
    top_recommendations: [],
    pages: [],
  };
});
const commercialPages = computed(() => (Array.isArray(commercialSummary.value?.pages) ? commercialSummary.value.pages : []));

const comparisonPayload = computed(() => {
  if (comparison.value && typeof comparison.value === "object") return comparison.value;
  if (audit.value?.comparison_preview && typeof audit.value.comparison_preview === "object") {
    return audit.value.comparison_preview;
  }
  return { has_data: false, reason: "Для сравнения нужен завершённый аудит по домену." };
});

const scoreValue = computed(() => Number(audit.value?.score ?? audit.value?.seo_score ?? 0) || 0);
const errorsCount = computed(() => breakdown.value.high_issues + breakdown.value.medium_issues + breakdown.value.low_issues);
const rawStatus = computed(() => String(audit.value?.status || "idle").trim().toLowerCase());
const isInProgress = computed(() => rawStatus.value === "pending" || rawStatus.value === "running");

const canStartAudit = computed(
  () => Boolean(domain.value) && !starting.value && !stopping.value && !loading.value && !bootstrapping.value && !isInProgress.value,
);
const canStopAudit = computed(() => Boolean(auditId.value) && !starting.value && !stopping.value && !bootstrapping.value && isInProgress.value);
const canExport = computed(() => Boolean(auditId.value) && !isInProgress.value && !exporting.value);
const canCompare = computed(() => Boolean(auditId.value) && rawStatus.value === "done" && historyRows.value.length > 0);

const runningHint = computed(() => (rawStatus.value === "pending" ? "Аудит в очереди..." : "Аудит выполняется..."));
const avgTtfbMs = computed(() => Number(audit.value?.avg_ttfb_ms ?? 0) || 0);
const avgPerformanceScore = computed(() => Number(audit.value?.avg_performance_score ?? 0) || 0);
const pagesWithSpeedIssues = computed(() => Number(audit.value?.pages_with_speed_issues ?? 0) || 0);
const pagesWithIndexingIssues = computed(() => Number(audit.value?.pages_with_indexing_issues ?? 0) || 0);
const hasRobotsTxt = computed(() => Boolean(audit.value?.has_robots_txt));
const hasSitemapXml = computed(() => Boolean(audit.value?.has_sitemap_xml));

const scoreClass = computed(() => scoreClassByValue(scoreValue.value));
const statusLabel = computed(() => {
  const labels = {
    idle: "Не запускался",
    pending: "В очереди",
    running: "Выполняется",
    done: "Готово",
    error: "Ошибка",
    stopped: "Остановлено",
  };
  return labels[rawStatus.value] || rawStatus.value;
});
const statusClass = computed(() => {
  if (rawStatus.value === "done") return "status-done";
  if (rawStatus.value === "error") return "status-error";
  if (rawStatus.value === "stopped") return "status-stopped";
  if (isInProgress.value) return "status-running";
  return "status-idle";
});

function canUseStorage() {
  return typeof window !== "undefined" && typeof window.localStorage !== "undefined";
}
function persistState() {
  if (!canUseStorage()) return;
  try {
    if (auditId.value) window.localStorage.setItem(STORAGE_AUDIT_ID_KEY, String(auditId.value));
    else window.localStorage.removeItem(STORAGE_AUDIT_ID_KEY);
    window.localStorage.setItem(STORAGE_DOMAIN_KEY, String(domain.value || ""));
  } catch {
    // ignore
  }
}
function clearPersistedAuditId() {
  if (!canUseStorage()) return;
  try {
    window.localStorage.removeItem(STORAGE_AUDIT_ID_KEY);
  } catch {
    // ignore
  }
}
function restoreState() {
  if (!canUseStorage()) return;
  try {
    const storedId = String(window.localStorage.getItem(STORAGE_AUDIT_ID_KEY) || "").trim();
    const storedDomain = String(window.localStorage.getItem(STORAGE_DOMAIN_KEY) || "").trim();
    if (storedDomain) domain.value = storedDomain;
    if (/^\d+$/.test(storedId)) auditId.value = Number(storedId);
  } catch {
    // ignore
  }
}

function severityLabel(value) {
  const key = String(value || "").toLowerCase();
  if (key === "high") return "Критичный";
  if (key === "medium") return "Средний";
  if (key === "low") return "Низкий";
  return "—";
}
function issueLabel(issue) {
  return String(issue?.issue_title || "").trim() || "SEO-ошибка";
}
function formatMs(value) {
  const num = Number(value || 0);
  if (num <= 0) return "—";
  return `${Math.round(num)} мс`;
}
function formatBytes(value) {
  const num = Number(value || 0);
  if (num <= 0) return "—";
  if (num >= 1024 * 1024) return `${(num / (1024 * 1024)).toFixed(2)} MB`;
  if (num >= 1024) return `${(num / 1024).toFixed(1)} KB`;
  return `${num} B`;
}
function formatDate(value) {
  const raw = String(value || "").trim();
  if (!raw) return "—";
  const date = new Date(raw);
  if (Number.isNaN(date.getTime())) return raw;
  return new Intl.DateTimeFormat("ru-RU", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}
function signedDelta(value) {
  const num = Number(value || 0);
  if (num > 0) return `+${num}`;
  if (num < 0) return `${num}`;
  return "0";
}
function yesNo(value) {
  return value ? "Да" : "Нет";
}
function scoreClassByValue(value) {
  const score = Number(value || 0);
  if (score <= 40) return "seo-score-bad";
  if (score <= 70) return "seo-score-warn";
  return "seo-score-good";
}
function speedStatusLabel(value) {
  const key = String(value || "").toLowerCase();
  if (key === "good") return "Хорошо";
  if (key === "warning") return "Замечания";
  if (key === "critical") return "Критично";
  return "Неизвестно";
}
function speedStatusClass(value) {
  const key = String(value || "").toLowerCase();
  if (key === "good") return "severity-low";
  if (key === "warning") return "severity-medium";
  if (key === "critical") return "severity-high";
  return "";
}
function indexabilityStatusLabel(value) {
  const key = String(value || "").toLowerCase();
  if (key === "indexable") return "Индексируется";
  if (key === "noindex") return "Noindex";
  if (key === "blocked") return "Блок robots";
  if (key === "conflict") return "Конфликт";
  return "Неизвестно";
}
function indexabilityStatusClass(value) {
  const key = String(value || "").toLowerCase();
  if (key === "indexable") return "severity-low";
  if (key === "noindex") return "severity-medium";
  if (key === "blocked" || key === "conflict") return "severity-high";
  return "";
}
function pageSpeedIssues(page) {
  const url = String(page?.url || "");
  return speedIssues.value.filter((item) => String(item?.page_url || "") === url);
}
function pageIndexingIssues(page) {
  const url = String(page?.url || "");
  return indexingIssues.value.filter((item) => String(item?.page_url || "") === url);
}
function priorityClass(value) {
  const key = String(value || "").toLowerCase();
  if (key === "urgent") return "priority-urgent";
  if (key === "important") return "priority-important";
  return "priority-later";
}
function signalClass(value) {
  return value ? "signal-ok" : "signal-missing";
}
function commercialStatusClass(value) {
  const key = String(value || "").toLowerCase();
  if (key === "good") return "severity-low";
  if (key === "warning") return "severity-medium";
  if (key === "critical") return "severity-high";
  return "";
}
function commercialStatusLabel(value) {
  const key = String(value || "").toLowerCase();
  if (key === "good") return "Готова к заявкам";
  if (key === "warning") return "Есть замечания";
  if (key === "critical") return "Слабо подготовлена";
  return "Есть замечания";
}
function comparisonTrendClass(value) {
  const key = String(value || "").toLowerCase();
  if (key === "better") return "trend-better";
  if (key === "worse") return "trend-worse";
  return "trend-stable";
}
function boolTransitionLabel(value) {
  const key = String(value || "").toLowerCase();
  if (key === "appeared") return "Появился";
  if (key === "missing_now") return "Пропал";
  return "Без изменений";
}
function toggleBlock(key) {
  collapsed.value = { ...collapsed.value, [key]: !collapsed.value[key] };
}
function toggleIssueGroupPages(issueType) {
  const key = String(issueType || "");
  if (!key) return;
  expandedIssueGroups.value = { ...expandedIssueGroups.value, [key]: !expandedIssueGroups.value[key] };
}
function isIssueGroupExpanded(issueType) {
  return Boolean(expandedIssueGroups.value[String(issueType || "")]);
}
function stopPolling() {
  if (pollTimer) {
    clearTimeout(pollTimer);
    pollTimer = null;
  }
}
function schedulePollingIfNeeded() {
  stopPolling();
  if (!auditId.value || !isInProgress.value) return;
  pollTimer = setTimeout(() => {
    void loadAudit({ silent: true });
  }, POLL_INTERVAL_MS);
}

async function loadHistory() {
  if (!auditId.value) return;
  try {
    const { data } = await api.get(`/api/seo/${auditId.value}/history/`);
    historyRows.value = Array.isArray(data?.rows) ? data.rows : [];
    if (!selectedCompareAuditId.value && data?.default_compare_audit_id) {
      selectedCompareAuditId.value = String(data.default_compare_audit_id);
    }
  } catch {
    historyRows.value = Array.isArray(audit.value?.audit_history) ? audit.value.audit_history : [];
  }
}

async function loadAudit({ silent = false, allowLatestFallback = true } = {}) {
  if (!auditId.value) return;
  if (!silent) loading.value = true;
  error.value = "";
  try {
    const { data } = await api.get(`/api/seo/${auditId.value}/`);
    audit.value = data || null;
    if (data?.domain) domain.value = String(data.domain);
    historyRows.value = Array.isArray(data?.audit_history) ? data.audit_history : [];
    if (!selectedCompareAuditId.value && historyRows.value.length) {
      selectedCompareAuditId.value = String(historyRows.value[0].audit_id || "");
    }
    comparison.value = data?.comparison_preview || null;
    persistState();
    if (rawStatus.value === "done") {
      await loadHistory();
    }
  } catch (e) {
    const responseStatus = Number(e?.response?.status || 0);
    if (responseStatus === 404 && allowLatestFallback) {
      auditId.value = null;
      audit.value = null;
      historyRows.value = [];
      selectedCompareAuditId.value = "";
      comparison.value = null;
      clearPersistedAuditId();
      const loadedLatest = await loadLatestAudit({ silent: true, preferCurrentDomain: true, suppressError: true });
      if (loadedLatest) return;
    }
    error.value = e?.response?.data?.detail || "Не удалось загрузить результат аудита.";
  } finally {
    if (!silent) loading.value = false;
    schedulePollingIfNeeded();
  }
}

async function loadLatestAudit({ silent = false, preferCurrentDomain = false, suppressError = false } = {}) {
  if (!silent) loading.value = true;
  try {
    const params = preferCurrentDomain && String(domain.value || "").trim() ? { domain: String(domain.value).trim() } : undefined;
    const { data } = await api.get("/api/seo/latest/", { params });
    const latestAuditId = Number(data?.audit_id || 0) || null;
    if (!latestAuditId) {
      auditId.value = null;
      audit.value = null;
      historyRows.value = [];
      selectedCompareAuditId.value = "";
      comparison.value = null;
      persistState();
      return false;
    }
    auditId.value = latestAuditId;
    if (data?.domain) domain.value = String(data.domain);
    persistState();
    await loadAudit({ silent: true, allowLatestFallback: false });
    return true;
  } catch (e) {
    if (!suppressError) error.value = e?.response?.data?.detail || "Не удалось загрузить последний SEO-аудит.";
    return false;
  } finally {
    if (!silent) loading.value = false;
  }
}

async function startAudit() {
  if (!canStartAudit.value) return;
  error.value = "";
  starting.value = true;
  stopPolling();
  try {
    const { data } = await api.post("/api/seo/start/", { domain: domain.value });
    auditId.value = Number(data?.audit_id || 0) || null;
    if (data?.domain) domain.value = String(data.domain);
    historyRows.value = [];
    selectedCompareAuditId.value = "";
    comparison.value = null;
    persistState();
    await loadAudit();
  } catch (e) {
    error.value = e?.response?.data?.detail || "Не удалось запустить аудит.";
  } finally {
    starting.value = false;
  }
}

async function stopAudit() {
  if (!canStopAudit.value) return;
  stopping.value = true;
  error.value = "";
  stopPolling();
  try {
    await api.post(`/api/seo/${auditId.value}/stop/`);
    await loadAudit({ silent: true });
  } catch (e) {
    error.value = e?.response?.data?.detail || "Не удалось остановить аудит.";
  } finally {
    stopping.value = false;
  }
}

async function compareAudits() {
  if (!auditId.value || rawStatus.value !== "done") return;
  comparisonLoading.value = true;
  error.value = "";
  try {
    const params = {};
    const selected = String(selectedCompareAuditId.value || "").trim();
    if (selected) params.with_audit_id = selected;
    const { data } = await api.get(`/api/seo/${auditId.value}/compare/`, { params });
    comparison.value = data || null;
  } catch (e) {
    error.value = e?.response?.data?.detail || "Не удалось выполнить сравнение.";
  } finally {
    comparisonLoading.value = false;
  }
}

async function exportReport() {
  if (!canExport.value) return;
  exporting.value = true;
  error.value = "";
  try {
    const params = {};
    const selected = String(selectedCompareAuditId.value || "").trim();
    if (selected) params.with_audit_id = selected;
    const response = await api.get(`/api/seo/${auditId.value}/export/`, { params, headers: { Accept: "text/csv" } });
    const contentDisposition = response?.headers?.get?.("content-disposition") || "";
    const match = /filename=\"?([^\";]+)\"?/i.exec(contentDisposition);
    const filename = match?.[1] || `seo-audit-${auditId.value}.csv`;
    let payload = response?.data;
    if (typeof payload === "undefined" || payload === null) payload = "";
    if (typeof payload !== "string") payload = JSON.stringify(payload, null, 2);
    const blob = new Blob([payload], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  } catch (e) {
    error.value = e?.response?.data?.detail || "Не удалось экспортировать отчёт.";
  } finally {
    exporting.value = false;
  }
}

async function manualRefresh() {
  if (auditId.value) await loadAudit();
  else await loadLatestAudit({ preferCurrentDomain: true });
}

defineExpose({ manualRefresh });

onMounted(() => {
  restoreState();
  bootstrapping.value = true;
  const bootstrap = async () => {
    if (auditId.value) await loadAudit({ silent: true });
    else await loadLatestAudit({ silent: true, preferCurrentDomain: true, suppressError: true });
  };
  void bootstrap().finally(() => {
    bootstrapping.value = false;
  });
});

onBeforeUnmount(() => {
  stopPolling();
});
</script>
<style scoped>
.card-head-wrap {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.seo-start-row {
  display: grid;
  grid-template-columns: minmax(16rem, 30rem) auto auto;
  gap: 0.75rem;
  align-items: end;
}

.seo-field {
  display: grid;
  gap: 0.35rem;
}

.seo-field-label {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--color-muted);
}

.seo-input,
.seo-select {
  min-height: 2.6rem;
  border-radius: 0.65rem;
  border: 1px solid var(--color-border);
  padding: 0.5rem 0.75rem;
  font: inherit;
  width: 100%;
}

.seo-start-btn,
.seo-stop-btn,
.seo-export-btn,
.seo-compare-btn,
.collapse-btn,
.issue-pages-toggle {
  min-height: 2.6rem;
  border-radius: 0.65rem;
  border: 1px solid var(--color-border);
  padding: 0 0.9rem;
  font-weight: 600;
  cursor: pointer;
  background: #fff;
  color: #050505;
}

.seo-start-btn {
  border-color: transparent;
  color: #fff;
  background: linear-gradient(135deg, #0284c7, #2563eb);
}

.seo-start-btn.is-busy {
  background: linear-gradient(135deg, #64748b, #334155);
}

.seo-stop-btn {
  border-color: #fecaca;
  background: #fef2f2;
  color: #b91c1c;
}

.seo-export-btn,
.seo-compare-btn {
  border-color: #bfdbfe;
  background: #eff6ff;
  color: #1e40af;
}

.collapse-btn,
.issue-pages-toggle {
  min-height: 2rem;
  border-radius: 999px;
}

.seo-start-btn:disabled,
.seo-stop-btn:disabled,
.seo-export-btn:disabled,
.seo-compare-btn:disabled,
.collapse-btn:disabled,
.issue-pages-toggle:disabled {
  opacity: 0.65;
  cursor: default;
}

.seo-running-indicator {
  margin: 0.7rem 0 0;
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  color: #1d4ed8;
  font-weight: 600;
}

.seo-spinner {
  width: 0.95rem;
  height: 0.95rem;
  border-radius: 999px;
  border: 2px solid #bfdbfe;
  border-top-color: #1d4ed8;
  animation: seo-spin 0.9s linear infinite;
}

.seo-hint {
  margin: 0.7rem 0 0;
}

.seo-stats {
  margin-top: 16px;
}

.seo-breakdown-grid,
.comparison-grid,
.commercial-summary-grid {
  display: grid;
  gap: 0.75rem;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.seo-breakdown-card,
.comparison-card,
.commercial-summary-card,
.fix-plan-item {
  border: 1px solid var(--color-border);
  border-radius: 0.8rem;
  padding: 0.75rem;
}

.seo-breakdown-card span,
.comparison-card span,
.commercial-summary-card span {
  font-size: 0.82rem;
  color: var(--color-muted);
}

.seo-breakdown-high {
  background: #fff7f7;
}

.seo-breakdown-medium {
  background: #fffaf0;
}

.seo-breakdown-low {
  background: #f5fbf6;
}

.block-hint {
  margin: 0 0 0.7rem;
}

.fix-plan-list,
.issue-pages-list,
.comparison-wrap,
.signal-grid {
  display: grid;
  gap: 0.5rem;
}

.fix-plan-head,
.fix-plan-meta,
.indexing-summary,
.comparison-index-files,
.issue-filters {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.priority-pill,
.severity-pill,
.signal-grid span {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 700;
  padding: 0.15rem 0.55rem;
}

.priority-urgent,
.severity-high,
.signal-missing {
  color: #991b1b;
  background: #fee2e2;
}

.priority-important,
.severity-medium {
  color: #92400e;
  background: #fef3c7;
}

.priority-later {
  color: #1e40af;
  background: #dbeafe;
}

.severity-low,
.signal-ok {
  color: #166534;
  background: #dcfce7;
}

.issue-pages-list span {
  border: 1px solid var(--color-border);
  border-radius: 0.55rem;
  padding: 0.35rem 0.45rem;
  font-size: 0.82rem;
  word-break: break-word;
}

.compare-controls {
  margin-bottom: 0.75rem;
  max-width: 30rem;
}

.comparison-lists {
  display: grid;
  gap: 0.75rem;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.comparison-issue-list,
.recommendation-mini-list,
.recommendation-list ul {
  margin: 0;
  padding-left: 1rem;
  display: grid;
  gap: 0.35rem;
}

.recommendation-list {
  margin-bottom: 0.75rem;
}

.signal-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.url-cell {
  max-width: 20rem;
  word-break: break-word;
}

.issue-inline-list {
  font-size: 0.82rem;
  color: var(--color-muted);
}

.issue-filter-btn {
  min-height: 2rem;
  border: 1px solid var(--color-border);
  border-radius: 999px;
  padding: 0 0.7rem;
  background: #fff;
  font-weight: 600;
  cursor: pointer;
  color: #050505;
}

.issue-filter-btn.active {
  border-color: #1d4ed8;
  background: #eff6ff;
  color: #1e40af;
}

.status-done {
  color: #15803d;
}

.status-error {
  color: #b91c1c;
}

.status-running {
  color: #1d4ed8;
}

.status-stopped,
.seo-score-warn {
  color: #b45309;
}

.status-idle {
  color: #6b7280;
}

.seo-score-bad {
  color: #b91c1c;
}

.seo-score-good {
  color: #15803d;
}

.trend-better {
  color: #15803d;
}

.trend-worse {
  color: #b91c1c;
}

.trend-stable {
  color: #1e40af;
}

.empty-state {
  margin: 0;
}

@keyframes seo-spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 1100px) {
  .comparison-grid,
  .commercial-summary-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 960px) {
  .seo-start-row,
  .seo-breakdown-grid,
  .comparison-grid,
  .commercial-summary-grid,
  .comparison-lists,
  .signal-grid {
    grid-template-columns: 1fr;
  }

  .indexing-summary {
    flex-direction: column;
    gap: 0.35rem;
  }
}
</style>
