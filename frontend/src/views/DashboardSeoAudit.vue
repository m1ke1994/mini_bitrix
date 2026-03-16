<template>
  <section class="dashboard-section seo-audit-page">
    <p v-if="error" class="error">{{ error }}</p>

    <div id="seo-overview" class="chart-card seo-section-card seo-overview-card">
      <div class="card-head card-head-wrap">
        <div class="section-headline">
          <h2>SEO-аудит сайта</h2>
          <p class="section-subtitle">
            Запустите аудит домена, чтобы увидеть технические проблемы, точки роста и приоритеты исправлений.
          </p>
        </div>
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
        Введите домен сайта. Аудит покажет технические проблемы, приоритеты исправлений и динамику изменений.
      </p>
    </div>

    <div v-if="auditId" class="chart-card seo-section-card seo-ai-card">
      <div class="card-head card-head-wrap">
        <div class="section-headline">
          <h2>AI-рекомендации по SEO</h2>
          <p class="section-subtitle">
            После завершения аудита сервис соберёт краткий вывод и структурированный план исправлений.
          </p>
        </div>
        <button
          type="button"
          class="seo-ai-refresh-btn"
          :disabled="!canRunSeoAiAnalysis"
          @click="runSeoAiAnalysis"
        >
          {{ seoAiLoading ? "Анализ..." : "Запустить AI-анализ SEO" }}
        </button>
      </div>

      <p v-if="isInProgress" class="muted">
        Сначала дождитесь завершения текущего SEO-аудита.
      </p>

      <template v-if="!seoAiStarted && !seoAiLoading">
        <div class="seo-empty-panel">
          <p class="muted seo-ai-placeholder">
            Рекомендации ещё не загружены. Нажмите «Запустить AI-анализ SEO», чтобы получить приоритетные задачи и
            пошаговые действия по исправлению найденных проблем.
          </p>
        </div>
      </template>

      <p v-else-if="seoAiLoading" class="muted">
        Анализируем результаты аудита и формируем рекомендации...
      </p>

      <template v-else-if="seoAiHasResult">
        <div class="seo-ai-summary-box">
          <p class="seo-ai-summary">{{ seoAiRecommendations.summary }}</p>

          <div class="seo-ai-meta">
            <span class="priority-pill" :class="seoAiPriorityClass(seoAiRecommendations.priority)">
              Приоритет: {{ seoAiPriorityLabel(seoAiRecommendations.priority) }}
            </span>
            <span class="seo-meta-chip">Источник: AI</span>
            <span v-if="seoAiRecommendations.cached" class="seo-meta-chip">Кэшированный ответ</span>
          </div>
        </div>

        <div v-if="seoAiOverviewChips.length" class="seo-ai-overview">
          <span
            v-for="(chip, idx) in seoAiOverviewChips"
            :key="`seo-ai-chip-${idx}`"
            class="seo-ai-overview-chip"
          >
            {{ chip }}
          </span>
        </div>

        <section v-if="seoAiHighlights.length" class="seo-ai-section">
          <h3>Краткий вывод</h3>
          <ul class="seo-ai-list">
            <li v-for="(item, idx) in seoAiHighlights" :key="`seo-ai-highlight-${idx}`">
              {{ item }}
            </li>
          </ul>
        </section>

        <section v-if="seoAiMetricsReview.length" class="seo-ai-section">
          <h3>Оценка ключевых показателей</h3>
          <div class="seo-ai-metrics-grid">
            <article
              v-for="(metric, idx) in seoAiMetricsReview"
              :key="`seo-ai-metric-${idx}-${metric.label}`"
              class="seo-ai-metric-card"
            >
              <div class="seo-ai-metric-head">
                <span>{{ metric.label }}</span>
                <span class="severity-pill" :class="seoMetricStatusClass(metric.status)">
                  {{ seoMetricStatusLabel(metric.status) }}
                </span>
              </div>
              <strong>{{ metric.value }}</strong>
              <p class="muted">{{ metric.comment }}</p>
            </article>
          </div>
        </section>

        <section v-if="seoAiProblems.length" class="seo-ai-section">
          <h3>Основные проблемы</h3>
          <div class="seo-ai-problems">
            <article
              v-for="(problem, idx) in seoAiProblems"
              :key="`seo-ai-problem-${idx}-${problem.title}`"
              class="seo-ai-problem-item"
            >
              <div class="seo-ai-problem-head">
                <strong>{{ problem.title }}</strong>
                <span class="severity-pill" :class="`severity-${problem.severity}`">
                  {{ severityLabel(problem.severity) }}
                </span>
              </div>
              <p class="muted">{{ problem.description }}</p>
            </article>
          </div>
        </section>

        <section v-if="seoAiFixPlan.length" class="seo-ai-section">
          <h3>План исправлений</h3>
          <ol class="seo-ai-fix-plan">
            <li v-for="(step, idx) in seoAiFixPlan" :key="`seo-ai-fix-${idx}-${step.title}`">
              <div class="seo-ai-fix-head">
                <span class="seo-ai-step">Шаг {{ step.step }}</span>
                <strong>{{ step.title }}</strong>
              </div>
              <p class="muted">{{ step.details }}</p>
            </li>
          </ol>
        </section>

        <section class="seo-ai-section">
          <h3>Что именно исправить</h3>
          <ul v-if="seoAiActionItems.length" class="seo-ai-list">
            <li v-for="(item, idx) in seoAiActionItems" :key="`seo-ai-action-${idx}`">
              {{ item }}
            </li>
          </ul>
          <p v-else class="muted empty-state">
            AI не вернул список действий. Запустите анализ ещё раз.
          </p>
        </section>
      </template>

      <p v-else class="muted seo-ai-error">{{ seoAiFailureMessage }}</p>
    </div>

    <div v-if="auditId" class="seo-anchor-nav-wrap">
      <nav class="seo-anchor-nav" aria-label="Разделы SEO-аудита">
        <button
          v-for="item in seoSectionNavItems"
          :key="item.id"
          type="button"
          class="seo-anchor-nav-btn"
          :class="{ active: activeSeoSection === item.id }"
          @click="scrollToSeoSection(item.id)"
        >
          {{ item.label }}
        </button>
      </nav>
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

    <div id="seo-compare" v-if="auditId" class="chart-card seo-section-card">
      <div class="card-head card-head-wrap">
        <div class="section-headline">
          <h2>Сравнение аудитов во времени</h2>
          <p class="section-subtitle">
            Здесь пользователь видит, что улучшилось, что ухудшилось и где сайт остался без изменений.
          </p>
        </div>
        <button
          type="button"
          class="seo-compare-btn"
          :disabled="!canCompare || comparisonLoading"
          @click="compareAudits"
        >
          {{ comparisonLoading ? "Сравнение..." : "Сравнить аудит" }}
        </button>
      </div>

      <div v-if="historyRows.length" class="compare-controls">
        <label class="seo-field">
          <span class="seo-field-label">Сравнить с аудитом</span>
          <select v-model="selectedCompareAuditId" class="seo-select">
            <option
              v-for="item in historyRows"
              :key="`history-${item.audit_id}`"
              :value="String(item.audit_id)"
            >
              #{{ item.audit_id }} · {{ formatDate(item.created_at) }} · SEO {{ item.score }}
            </option>
          </select>
        </label>
      </div>

      <div v-if="comparisonPayload?.has_data" class="comparison-wrap">
        <div class="comparison-topline">
          <p class="comparison-trend" :class="comparisonTrendClass(comparisonPayload?.trend)">
            {{ comparisonTrendLabel(comparisonPayload) }}
          </p>
          <span class="comparison-note muted">Сравнение текущего аудита с выбранным предыдущим отчётом</span>
        </div>

        <div class="comparison-grid">
          <article class="comparison-card comparison-card-featured">
            <div class="comparison-card-head">
              <span>SEO-оценка</span>
              <strong :class="scoreClassByValue(comparisonPayload.score?.after)">
                {{ comparisonPayload.score?.after ?? 0 }}
              </strong>
            </div>
            <div class="comparison-values">
              <div>
                <small>Было</small>
                <b>{{ comparisonPayload.score?.before ?? 0 }}</b>
              </div>
              <div>
                <small>Стало</small>
                <b>{{ comparisonPayload.score?.after ?? 0 }}</b>
              </div>
              <div>
                <small>Изменение</small>
                <b :class="deltaClass(comparisonPayload.score?.delta)">
                  {{ compareDelta(comparisonPayload.score) }}
                </b>
              </div>
            </div>
          </article>

          <article class="comparison-card">
            <div class="comparison-card-head">
              <span>Критичные ошибки</span>
              <strong>{{ comparisonPayload.issues?.high?.after ?? 0 }}</strong>
            </div>
            <div class="comparison-values">
              <div>
                <small>Было</small>
                <b>{{ comparisonPayload.issues?.high?.before ?? 0 }}</b>
              </div>
              <div>
                <small>Стало</small>
                <b>{{ comparisonPayload.issues?.high?.after ?? 0 }}</b>
              </div>
              <div>
                <small>Изменение</small>
                <b :class="deltaClass(reverseDelta(comparisonPayload.issues?.high?.delta))">
                  {{ compareDelta(comparisonPayload.issues?.high) }}
                </b>
              </div>
            </div>
          </article>

          <article class="comparison-card">
            <div class="comparison-card-head">
              <span>Средние ошибки</span>
              <strong>{{ comparisonPayload.issues?.medium?.after ?? 0 }}</strong>
            </div>
            <div class="comparison-values">
              <div>
                <small>Было</small>
                <b>{{ comparisonPayload.issues?.medium?.before ?? 0 }}</b>
              </div>
              <div>
                <small>Стало</small>
                <b>{{ comparisonPayload.issues?.medium?.after ?? 0 }}</b>
              </div>
              <div>
                <small>Изменение</small>
                <b :class="deltaClass(reverseDelta(comparisonPayload.issues?.medium?.delta))">
                  {{ compareDelta(comparisonPayload.issues?.medium) }}
                </b>
              </div>
            </div>
          </article>

          <article class="comparison-card">
            <div class="comparison-card-head">
              <span>Низкие ошибки</span>
              <strong>{{ comparisonPayload.issues?.low?.after ?? 0 }}</strong>
            </div>
            <div class="comparison-values">
              <div>
                <small>Было</small>
                <b>{{ comparisonPayload.issues?.low?.before ?? 0 }}</b>
              </div>
              <div>
                <small>Стало</small>
                <b>{{ comparisonPayload.issues?.low?.after ?? 0 }}</b>
              </div>
              <div>
                <small>Изменение</small>
                <b :class="deltaClass(reverseDelta(comparisonPayload.issues?.low?.delta))">
                  {{ compareDelta(comparisonPayload.issues?.low) }}
                </b>
              </div>
            </div>
          </article>

          <article class="comparison-card">
            <div class="comparison-card-head">
              <span>Проблемы скорости</span>
              <strong>{{ comparisonPayload.speed_pages?.after ?? 0 }}</strong>
            </div>
            <div class="comparison-values">
              <div>
                <small>Было</small>
                <b>{{ comparisonPayload.speed_pages?.before ?? 0 }}</b>
              </div>
              <div>
                <small>Стало</small>
                <b>{{ comparisonPayload.speed_pages?.after ?? 0 }}</b>
              </div>
              <div>
                <small>Изменение</small>
                <b :class="deltaClass(reverseDelta(comparisonPayload.speed_pages?.delta))">
                  {{ compareDelta(comparisonPayload.speed_pages) }}
                </b>
              </div>
            </div>
          </article>

          <article class="comparison-card">
            <div class="comparison-card-head">
              <span>Проблемы индексации</span>
              <strong>{{ comparisonPayload.indexing_pages?.after ?? 0 }}</strong>
            </div>
            <div class="comparison-values">
              <div>
                <small>Было</small>
                <b>{{ comparisonPayload.indexing_pages?.before ?? 0 }}</b>
              </div>
              <div>
                <small>Стало</small>
                <b>{{ comparisonPayload.indexing_pages?.after ?? 0 }}</b>
              </div>
              <div>
                <small>Изменение</small>
                <b :class="deltaClass(reverseDelta(comparisonPayload.indexing_pages?.delta))">
                  {{ compareDelta(comparisonPayload.indexing_pages) }}
                </b>
              </div>
            </div>
          </article>
        </div>

        <div class="comparison-index-files">
          <article class="comparison-file-card">
            <span class="muted">robots.txt</span>
            <strong>{{ boolTransitionLabel(comparisonPayload.robots_txt?.status) }}</strong>
          </article>
          <article class="comparison-file-card">
            <span class="muted">sitemap.xml</span>
            <strong>{{ boolTransitionLabel(comparisonPayload.sitemap_xml?.status) }}</strong>
          </article>
        </div>

        <div class="comparison-lists">
          <article class="comparison-list-card">
            <div class="comparison-list-head">
              <h3>Новые проблемы</h3>
              <span class="comparison-counter comparison-counter-warn">
                {{ comparisonPayload.new_issues_count }} шт.
              </span>
            </div>

            <ul v-if="comparisonPayload.new_issues?.length" class="comparison-issue-list">
              <li
                v-for="item in comparisonPayload.new_issues"
                :key="`new-${item.issue_type}-${item.page_url}`"
              >
                <strong>{{ item.issue_title }}</strong>
                <span>{{ item.page_url }}</span>
              </li>
            </ul>
            <p v-else class="muted">Новых проблем не найдено.</p>
          </article>

          <article class="comparison-list-card">
            <div class="comparison-list-head">
              <h3>Исправленные проблемы</h3>
              <span class="comparison-counter comparison-counter-good">
                {{ comparisonPayload.fixed_issues_count }} шт.
              </span>
            </div>

            <ul v-if="comparisonPayload.fixed_issues?.length" class="comparison-issue-list">
              <li
                v-for="item in comparisonPayload.fixed_issues"
                :key="`fixed-${item.issue_type}-${item.page_url}`"
              >
                <strong>{{ item.issue_title }}</strong>
                <span>{{ item.page_url }}</span>
              </li>
            </ul>
            <p v-else class="muted">Исправленных проблем пока нет.</p>
          </article>
        </div>
      </div>

      <p v-else class="muted empty-state">
        {{ comparisonPayload?.reason || "Для сравнения нужен завершённый аудит." }}
      </p>
    </div>

    <div id="seo-performance" v-if="auditId" class="chart-card seo-section-card">
      <div class="card-head card-head-wrap">
        <div class="section-headline">
          <h2>Скорость и производительность</h2>
          <p class="section-subtitle">
            Оценка строится по времени ответа, весу страницы и объёму подключённых ресурсов.
          </p>
        </div>
        <button type="button" class="collapse-btn" @click="toggleBlock('speed')">
          {{ collapsed.speed ? "Развернуть" : "Свернуть" }}
        </button>
      </div>

      <div class="inline-summary-chips">
        <span class="summary-chip">Проверено страниц: {{ pages.length }}</span>
        <span class="summary-chip">Со скоростными проблемами: {{ pagesWithSpeedIssues }}</span>
      </div>

      <template v-if="!collapsed.speed">
        <div class="table-wrap responsive-table-wrap">
          <table class="table mobile-stack-table">
            <thead>
              <tr>
                <th>URL</th>
                <th>Ответ сервера (TTFB)</th>
                <th>Размер HTML</th>
                <th>Файлы JS/CSS/изображения</th>
                <th>Вес JS/CSS/изображений</th>
                <th>Оценка</th>
                <th>Статус</th>
                <th>Проблемы</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="page in pages" :key="`speed-${page.id}`">
                <td data-label="URL" class="url-cell">{{ page.url }}</td>
                <td data-label="Ответ сервера (TTFB)">{{ formatMs(page.ttfb_ms) }}</td>
                <td data-label="Размер HTML">{{ formatBytes(page.html_size_bytes) }}</td>
                <td data-label="Файлы JS/CSS/изображения">
                  {{ page.js_files_count || 0 }} / {{ page.css_files_count || 0 }} / {{ page.images_count || 0 }}
                </td>
                <td data-label="Вес JS/CSS/изображений">
                  {{ formatBytes(page.total_js_bytes) }} /
                  {{ formatBytes(page.total_css_bytes) }} /
                  {{ formatBytes(page.total_image_bytes) }}
                </td>
                <td data-label="Оценка" :class="scoreClassByValue(page.performance_score)">
                  {{ page.performance_score ?? 0 }}
                </td>
                <td data-label="Статус">
                  <span class="severity-pill" :class="speedStatusClass(page.speed_status)">
                    {{ speedStatusLabel(page.speed_status) }}
                  </span>
                </td>
                <td data-label="Проблемы">
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

    <div id="seo-indexing" v-if="auditId" class="chart-card seo-section-card">
      <div class="card-head card-head-wrap">
        <div class="section-headline">
          <h2>Индексация</h2>
          <p class="section-subtitle">
            Проверка показывает, как поисковые системы видят и обходят страницы сайта.
          </p>
        </div>
        <button type="button" class="collapse-btn" @click="toggleBlock('indexing')">
          {{ collapsed.indexing ? "Развернуть" : "Свернуть" }}
        </button>
      </div>

      <div class="indexing-summary">
        <div class="summary-box">
          <span class="muted">robots.txt</span>
          <strong :class="hasRobotsTxt ? 'status-done' : 'status-error'">
            {{ hasRobotsTxt ? "доступен" : "не найден" }}
          </strong>
        </div>
        <div class="summary-box">
          <span class="muted">sitemap.xml</span>
          <strong :class="hasSitemapXml ? 'status-done' : 'status-error'">
            {{ hasSitemapXml ? "доступен" : "не найден или некорректен" }}
          </strong>
        </div>
        <div class="summary-box">
          <span class="muted">URL в sitemap</span>
          <strong>{{ audit?.sitemap_urls_count ?? 0 }}</strong>
        </div>
      </div>

      <template v-if="!collapsed.indexing">
        <div class="table-wrap responsive-table-wrap">
          <table class="table mobile-stack-table">
            <thead>
              <tr>
                <th>URL</th>
                <th>Мета-тег robots</th>
                <th>Canonical URL</th>
                <th>Индексация</th>
                <th>В sitemap</th>
                <th>Блок robots</th>
                <th>Проблемы</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="page in pages" :key="`indexing-${page.id}`">
                <td data-label="URL" class="url-cell">{{ page.url }}</td>
                <td data-label="Мета-тег robots">{{ page.meta_robots || "—" }}</td>
                <td data-label="Canonical URL" class="url-cell">{{ page.canonical_url || "—" }}</td>
                <td data-label="Индексация">
                  <span class="severity-pill" :class="indexabilityStatusClass(page.indexability_status)">
                    {{ indexabilityStatusLabel(page.indexability_status) }}
                  </span>
                </td>
                <td data-label="В sitemap">{{ yesNo(page.in_sitemap) }}</td>
                <td data-label="Блок robots">{{ yesNo(page.blocked_by_robots) }}</td>
                <td data-label="Проблемы">
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

    <div id="seo-pages" v-if="auditId" class="chart-card seo-section-card">
      <div class="card-head card-head-wrap">
        <div class="section-headline">
          <h2>Страницы</h2>
          <p class="section-subtitle">
            Базовая таблица по ключевым SEO-параметрам каждой страницы сайта.
          </p>
        </div>
        <button type="button" class="collapse-btn" @click="toggleBlock('pages')">
          {{ collapsed.pages ? "Развернуть" : "Свернуть" }}
        </button>
      </div>

      <div class="inline-summary-chips">
        <span class="summary-chip">Всего страниц в отчёте: {{ pages.length }}</span>
      </div>

      <template v-if="!collapsed.pages">
        <div class="table-wrap responsive-table-wrap">
          <table class="table mobile-stack-table">
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
                <td data-label="URL" class="url-cell">{{ page.url }}</td>
                <td data-label="Код ответа">{{ page.status_code }}</td>
                <td data-label="Title">{{ page.title || "—" }}</td>
                <td data-label="Длина Title">{{ page.title_length }}</td>
                <td data-label="Длина Description">{{ page.description_length }}</td>
                <td data-label="H1">{{ page.h1 || "—" }}</td>
                <td data-label="Количество H1">{{ page.h1_count }}</td>
                <td data-label="Слов">{{ page.word_count }}</td>
              </tr>
              <tr v-if="!pages.length">
                <td colspan="8">Пока нет данных по страницам.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
    </div>

    <div id="seo-errors" v-if="auditId" class="chart-card seo-section-card">
      <div class="card-head card-head-wrap">
        <div class="section-headline">
          <h2>Ошибки</h2>
          <p class="section-subtitle">
            Подробный список ошибок по страницам с фильтрами для быстрого поиска проблемных зон.
          </p>
        </div>
        <button type="button" class="collapse-btn" @click="toggleBlock('errors')">
          {{ collapsed.errors ? "Развернуть" : "Свернуть" }}
        </button>
      </div>

      <div class="inline-summary-chips">
        <span class="summary-chip">Всего ошибок: {{ errorsCount }}</span>
        <span class="summary-chip">Критичных: {{ breakdown.high_issues }}</span>
        <span class="summary-chip">Средних: {{ breakdown.medium_issues }}</span>
        <span class="summary-chip">Низких: {{ breakdown.low_issues }}</span>
      </div>

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

        <div class="table-wrap responsive-table-wrap">
          <table class="table mobile-stack-table">
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
                <td data-label="Страница" class="url-cell">{{ issue.page_url }}</td>
                <td data-label="Тип">{{ issueLabel(issue) }}</td>
                <td data-label="Уровень">
                  <span class="severity-pill" :class="`severity-${issue.severity}`">
                    {{ severityLabel(issue.severity) }}
                  </span>
                </td>
                <td data-label="Рекомендация">{{ issue.recommendation }}</td>
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
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";

import { useAiRecommendations } from "../composables/useAiRecommendations";
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

const seoSectionNavItems = [
  { id: "seo-overview", label: "SEO-аудит сайта" },
  { id: "seo-compare", label: "Сравнение аудитов" },
  { id: "seo-performance", label: "Скорость и производительность" },
  { id: "seo-indexing", label: "Индексация" },
  { id: "seo-pages", label: "Страницы" },
  { id: "seo-errors", label: "Ошибки" },
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
const activeSeoSection = ref("seo-overview");
const seoAiStarted = ref(false);

const {
  recommendations: seoAiRecommendations,
  loading: seoAiLoading,
  error: seoAiError,
  loadAiRecommendations: loadSeoAiRecommendations,
  resetAiRecommendations: resetSeoAiRecommendations,
} = useAiRecommendations({
  endpoint: () => (auditId.value ? `/api/seo/${auditId.value}/ai-recommendations/` : ""),
  fallbackTitle: "Рекомендации временно недоступны",
  fallbackSummary: "Не удалось получить AI-анализ по SEO-аудиту. Попробуйте обновить позже.",
});

const collapsed = ref({
  speed: true,
  indexing: true,
  pages: true,
  errors: true,
});

let pollTimer = null;
let sectionScrollRaf = null;

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

const comparisonPayload = computed(() => {
  if (comparison.value && typeof comparison.value === "object") return comparison.value;
  if (audit.value?.comparison_preview && typeof audit.value.comparison_preview === "object") {
    return audit.value.comparison_preview;
  }
  return { has_data: false, reason: "Для сравнения нужен завершённый аудит по домену." };
});

const scoreValue = computed(() => Number(audit.value?.score ?? audit.value?.seo_score ?? 0) || 0);
const errorsCount = computed(
  () => breakdown.value.high_issues + breakdown.value.medium_issues + breakdown.value.low_issues,
);
const rawStatus = computed(() => String(audit.value?.status || "idle").trim().toLowerCase());
const isInProgress = computed(() => rawStatus.value === "pending" || rawStatus.value === "running");

const canStartAudit = computed(
  () =>
    Boolean(domain.value) &&
    !starting.value &&
    !stopping.value &&
    !loading.value &&
    !bootstrapping.value &&
    !isInProgress.value,
);
const canStopAudit = computed(
  () =>
    Boolean(auditId.value) &&
    !starting.value &&
    !stopping.value &&
    !bootstrapping.value &&
    isInProgress.value,
);
const canExport = computed(() => Boolean(auditId.value) && !isInProgress.value && !exporting.value);
const canCompare = computed(
  () => Boolean(auditId.value) && rawStatus.value === "done" && historyRows.value.length > 0,
);
const canRunSeoAiAnalysis = computed(
  () => Boolean(auditId.value) && rawStatus.value === "done" && !seoAiLoading.value,
);

const seoAiHasResult = computed(
  () =>
    Boolean(seoAiRecommendations.value?.success) &&
    String(seoAiRecommendations.value?.source || "").trim().toLowerCase() === "ai",
);

const seoAiFailureMessage = computed(() => {
  const fromRequest = String(seoAiError.value || "").trim();
  if (fromRequest) return fromRequest;
  const fromPayload = String(seoAiRecommendations.value?.summary || "").trim();
  if (fromPayload && !seoAiHasResult.value) return fromPayload;
  return "Не удалось получить AI-рекомендации. Попробуйте запустить анализ ещё раз.";
});

const runningHint = computed(() =>
  rawStatus.value === "pending" ? "Аудит в очереди..." : "Аудит выполняется...",
);
const avgTtfbMs = computed(() => Number(audit.value?.avg_ttfb_ms ?? 0) || 0);
const avgPerformanceScore = computed(() => Number(audit.value?.avg_performance_score ?? 0) || 0);
const pagesWithSpeedIssues = computed(() => Number(audit.value?.pages_with_speed_issues ?? 0) || 0);
const pagesWithIndexingIssues = computed(
  () => Number(audit.value?.pages_with_indexing_issues ?? 0) || 0,
);
const hasRobotsTxt = computed(() => Boolean(audit.value?.has_robots_txt));
const hasSitemapXml = computed(() => Boolean(audit.value?.has_sitemap_xml));

const seoAiOverviewChips = computed(() => {
  const overview = seoAiRecommendations.value?.overview;
  if (!overview || typeof overview !== "object") return [];
  const map = [
    { key: "seo_score_label", label: "SEO-оценка" },
    { key: "pages_checked_label", label: "Страниц проверено" },
    { key: "errors_label", label: "Ошибки" },
    { key: "speed_label", label: "Скорость" },
    { key: "indexing_label", label: "Индексация" },
  ];
  return map
    .map((item) => {
      const value = String(overview[item.key] || "").trim();
      if (!value) return "";
      return `${item.label}: ${value}`;
    })
    .filter((item) => Boolean(item));
});

const seoAiHighlights = computed(() => normalizeTextList(seoAiRecommendations.value?.highlights, 5));

const seoAiMetricsReview = computed(() => {
  if (!Array.isArray(seoAiRecommendations.value?.metrics_review)) return [];
  return seoAiRecommendations.value.metrics_review
    .map((item) => ({
      label: String(item?.label || "").trim(),
      value: String(item?.value || "").trim(),
      status: normalizeSeoMetricStatus(item?.status),
      comment: String(item?.comment || "").trim(),
    }))
    .filter((item) => item.label && item.value)
    .slice(0, 8);
});

const seoAiProblems = computed(() => {
  if (!Array.isArray(seoAiRecommendations.value?.problems)) return [];
  return seoAiRecommendations.value.problems
    .map((item) => ({
      title: String(item?.title || "").trim(),
      severity: normalizeSeverity(item?.severity),
      description: String(item?.description || "").trim(),
    }))
    .filter((item) => item.title)
    .slice(0, 8);
});

const seoAiFixPlan = computed(() => {
  if (!Array.isArray(seoAiRecommendations.value?.fix_plan)) return [];
  return seoAiRecommendations.value.fix_plan
    .map((item, index) => {
      const step = Number(item?.step ?? index + 1);
      return {
        step: Number.isFinite(step) && step > 0 ? Math.round(step) : index + 1,
        title: String(item?.title || "").trim(),
        details: String(item?.details || "").trim(),
      };
    })
    .filter((item) => item.title)
    .sort((a, b) => a.step - b.step)
    .slice(0, 7);
});

const seoAiActionItems = computed(() => {
  const structured = normalizeTextList(seoAiRecommendations.value?.recommendations, 7);
  if (structured.length) return structured;
  return normalizeTextList(seoAiRecommendations.value?.items, 7);
});

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

function normalizeTextList(rows, maxItems = 7) {
  if (!Array.isArray(rows)) return [];
  return rows
    .map((item) => String(item || "").trim())
    .filter((item) => Boolean(item))
    .slice(0, maxItems);
}

function normalizeSeoMetricStatus(value) {
  const key = String(value || "").toLowerCase();
  if (key === "good" || key === "warning" || key === "bad" || key === "info") return key;
  return "info";
}

function normalizeSeverity(value) {
  const key = String(value || "").toLowerCase();
  if (key === "high" || key === "medium" || key === "low") return key;
  return "medium";
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
  if (num >= 1024 * 1024) return `${(num / (1024 * 1024)).toFixed(2)} МБ`;
  if (num >= 1024) return `${(num / 1024).toFixed(1)} КБ`;
  return `${num} Б`;
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

function compareDelta(metric) {
  const delta = Number(metric?.delta ?? 0) || 0;
  if (delta > 0) return `+${delta}`;
  if (delta < 0) return `${delta}`;
  return "0";
}

function comparisonTrendLabel(payload) {
  const key = String(payload?.trend || "").toLowerCase();
  if (key === "better") return "Стало лучше";
  if (key === "worse") return "Появились ухудшения";
  const explicitLabel = String(payload?.trend_label || "").trim();
  if (explicitLabel) return explicitLabel;
  return "Без заметных изменений";
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
  if (key === "noindex") return "Ограничена (noindex)";
  if (key === "blocked") return "Заблокирована robots.txt";
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

function seoAiPriorityLabel(value) {
  const key = String(value || "").toLowerCase();
  if (key === "high") return "Высокий";
  if (key === "low") return "Низкий";
  return "Средний";
}

function seoAiPriorityClass(value) {
  const key = String(value || "").toLowerCase();
  if (key === "high") return "priority-urgent";
  if (key === "low") return "priority-later";
  return "priority-important";
}

function seoMetricStatusLabel(value) {
  const key = String(value || "").toLowerCase();
  if (key === "good") return "Хорошо";
  if (key === "warning") return "Внимание";
  if (key === "bad") return "Проблема";
  return "Инфо";
}

function seoMetricStatusClass(value) {
  const key = String(value || "").toLowerCase();
  if (key === "good") return "severity-low";
  if (key === "warning") return "severity-medium";
  if (key === "bad") return "severity-high";
  return "seo-metric-status-info";
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

function reverseDelta(value) {
  const num = Number(value || 0) || 0;
  return num === 0 ? 0 : num * -1;
}

function deltaClass(value) {
  const num = Number(value || 0) || 0;
  if (num > 0) return "delta-positive";
  if (num < 0) return "delta-negative";
  return "delta-neutral";
}

function syncActiveSeoSection() {
  if (typeof document === "undefined") return;
  if (!auditId.value) {
    activeSeoSection.value = "seo-overview";
    return;
  }

  const offset = 150;
  let currentId = seoSectionNavItems[0].id;
  for (const item of seoSectionNavItems) {
    const node = document.getElementById(item.id);
    if (!node) continue;
    const top = node.getBoundingClientRect().top;
    if (top <= offset) currentId = item.id;
    else break;
  }
  activeSeoSection.value = currentId;
}

function handleSeoScroll() {
  if (typeof window === "undefined") return;
  if (sectionScrollRaf) return;
  sectionScrollRaf = window.requestAnimationFrame(() => {
    sectionScrollRaf = null;
    syncActiveSeoSection();
  });
}

function scrollToSeoSection(sectionId) {
  const targetId = String(sectionId || "").trim();
  if (!targetId || typeof document === "undefined") return;
  const node = document.getElementById(targetId);
  if (!node) return;
  activeSeoSection.value = targetId;
  node.scrollIntoView({ behavior: "smooth", block: "start" });
}

function toggleBlock(key) {
  collapsed.value = { ...collapsed.value, [key]: !collapsed.value[key] };
  if (typeof window !== "undefined") {
    window.setTimeout(() => {
      syncActiveSeoSection();
    }, 0);
  }
}

async function runSeoAiAnalysis() {
  if (!canRunSeoAiAnalysis.value) return;
  seoAiStarted.value = true;
  await loadSeoAiRecommendations({ force: true });
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
    } else {
      seoAiStarted.value = false;
      resetSeoAiRecommendations();
    }
    await nextTick();
    syncActiveSeoSection();
  } catch (e) {
    const responseStatus = Number(e?.response?.status || 0);
    if (responseStatus === 404 && allowLatestFallback) {
      auditId.value = null;
      audit.value = null;
      historyRows.value = [];
      selectedCompareAuditId.value = "";
      comparison.value = null;
      seoAiStarted.value = false;
      clearPersistedAuditId();
      resetSeoAiRecommendations();
      const loadedLatest = await loadLatestAudit({
        silent: true,
        preferCurrentDomain: true,
        suppressError: true,
      });
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
    const params =
      preferCurrentDomain && String(domain.value || "").trim()
        ? { domain: String(domain.value).trim() }
        : undefined;
    const { data } = await api.get("/api/seo/latest/", { params });
    const latestAuditId = Number(data?.audit_id || 0) || null;
    if (!latestAuditId) {
      auditId.value = null;
      audit.value = null;
      historyRows.value = [];
      selectedCompareAuditId.value = "";
      comparison.value = null;
      seoAiStarted.value = false;
      resetSeoAiRecommendations();
      persistState();
      return false;
    }
    auditId.value = latestAuditId;
    if (data?.domain) domain.value = String(data.domain);
    persistState();
    await loadAudit({ silent: true, allowLatestFallback: false });
    await nextTick();
    syncActiveSeoSection();
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
    seoAiStarted.value = false;
    resetSeoAiRecommendations();
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
    const response = await api.get(`/api/seo/${auditId.value}/export/`, {
      params,
      headers: { Accept: "text/csv" },
    });
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

watch(
  auditId,
  async (value, prevValue) => {
    if (value !== prevValue) {
      seoAiStarted.value = false;
      resetSeoAiRecommendations();
    }
    if (!value) {
      activeSeoSection.value = "seo-overview";
      seoAiStarted.value = false;
      resetSeoAiRecommendations();
      return;
    }
    await nextTick();
    syncActiveSeoSection();
  },
  { immediate: false },
);

defineExpose({ manualRefresh });

onMounted(() => {
  if (typeof window !== "undefined") {
    window.addEventListener("scroll", handleSeoScroll, { passive: true });
  }
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
  if (typeof window !== "undefined") {
    window.removeEventListener("scroll", handleSeoScroll);
  }
  if (sectionScrollRaf && typeof window !== "undefined") {
    window.cancelAnimationFrame(sectionScrollRaf);
    sectionScrollRaf = null;
  }
});
</script>

<style scoped>
.card-head-wrap {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.section-headline {
  display: grid;
  gap: 0.22rem;
}

.section-headline h2 {
  margin: 0;
}

.section-subtitle {
  margin: 0;
  font-size: 0.88rem;
  color: var(--color-muted);
  line-height: 1.45;
  max-width: 58rem;
}

.seo-overview-card {
  position: relative;
  overflow: hidden;
}

.seo-overview-card::before {
  content: "";
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at top left, rgba(59, 130, 246, 0.05), transparent 28%),
    radial-gradient(circle at right bottom, rgba(37, 99, 235, 0.04), transparent 24%);
  pointer-events: none;
}

.seo-start-row {
  display: grid;
  grid-template-columns: minmax(16rem, 30rem) auto auto;
  gap: 0.75rem;
  align-items: end;
  position: relative;
  z-index: 1;
}

.seo-field {
  display: grid;
  gap: 0.4rem;
}

.seo-field-label {
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--color-muted);
}

.seo-input,
.seo-select {
  min-height: 2.8rem;
  border-radius: 0.75rem;
  border: 1px solid var(--color-border);
  padding: 0.6rem 0.85rem;
  font: inherit;
  width: 100%;
  background: #fff;
  color: #111827;
}

.seo-input:focus,
.seo-select:focus {
  outline: none;
  border-color: #93c5fd;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.08);
}

.seo-start-btn,
.seo-stop-btn,
.seo-export-btn,
.seo-compare-btn,
.seo-ai-refresh-btn,
.collapse-btn,
.issue-pages-toggle {
  min-height: 2.75rem;
  border-radius: 0.75rem;
  border: 1px solid var(--color-border);
  padding: 0 1rem;
  font-weight: 700;
  cursor: pointer;
  background: #fff;
  color: #050505;
  transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease, background 0.18s ease;
}

.seo-start-btn:hover,
.seo-stop-btn:hover,
.seo-export-btn:hover,
.seo-compare-btn:hover,
.seo-ai-refresh-btn:hover,
.collapse-btn:hover,
.issue-filter-btn:hover,
.seo-anchor-nav-btn:hover {
  transform: translateY(-1px);
}

.seo-start-btn {
  border-color: transparent;
  color: #fff;
  background: linear-gradient(135deg, #0284c7, #2563eb);
  box-shadow: 0 10px 24px rgba(37, 99, 235, 0.18);
}

.seo-start-btn.is-busy {
  background: linear-gradient(135deg, #64748b, #334155);
  box-shadow: none;
}

.seo-stop-btn {
  border-color: #fecaca;
  background: #fff5f5;
  color: #b91c1c;
}

.seo-export-btn,
.seo-compare-btn,
.seo-ai-refresh-btn {
  border-color: #bfdbfe;
  background: #eff6ff;
  color: #1e40af;
}

.collapse-btn {
  min-height: 2.2rem;
  border-radius: 999px;
  padding: 0 0.95rem;
}

.seo-start-btn:disabled,
.seo-stop-btn:disabled,
.seo-export-btn:disabled,
.seo-compare-btn:disabled,
.seo-ai-refresh-btn:disabled,
.collapse-btn:disabled {
  opacity: 0.65;
  cursor: default;
  transform: none;
  box-shadow: none;
}

.seo-running-indicator {
  margin: 0.8rem 0 0;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: #1d4ed8;
  font-weight: 700;
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
  margin: 0.8rem 0 0;
  position: relative;
  z-index: 1;
}

.seo-section-card {
  scroll-margin-top: 6.7rem;
}

.seo-anchor-nav-wrap {
  position: sticky;
  top: 0.6rem;
  z-index: 16;
  margin: 0.95rem 0 1rem;
}

.seo-anchor-nav {
  display: flex;
  gap: 0.5rem;
  overflow-x: auto;
  padding: 0.52rem;
  border: 1px solid #dbe5f1;
  border-radius: 0.95rem;
  background: rgba(255, 255, 255, 0.94);
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 20px rgba(15, 23, 42, 0.05);
}

.seo-anchor-nav-btn {
  flex: 0 0 auto;
  min-height: 2.15rem;
  border: 1px solid #d1d9e6;
  border-radius: 999px;
  padding: 0 0.8rem;
  font-size: 0.79rem;
  font-weight: 700;
  color: #334155;
  background: #fff;
  cursor: pointer;
  transition: all 0.18s ease;
  white-space: nowrap;
}

.seo-anchor-nav-btn.active {
  border-color: #2563eb;
  background: #dbeafe;
  color: #1d4ed8;
  box-shadow: inset 0 0 0 1px rgba(37, 99, 235, 0.06);
}

.seo-stats {
  margin-top: 0.85rem;
  margin-bottom: 1rem;
}

.seo-stats .stat-card {
  border-radius: 1rem;
}

.inline-summary-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.55rem;
  margin-bottom: 0.8rem;
}

.summary-chip {
  display: inline-flex;
  align-items: center;
  min-height: 2rem;
  padding: 0.25rem 0.7rem;
  border-radius: 999px;
  font-size: 0.82rem;
  font-weight: 600;
  color: #1f2937;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
}

.comparison-wrap {
  display: grid;
  gap: 1rem;
}

.comparison-topline {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.8rem;
  flex-wrap: wrap;
}

.comparison-grid {
  display: grid;
  gap: 0.8rem;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.comparison-card {
  border: 1px solid var(--color-border);
  border-radius: 1rem;
  padding: 0.9rem;
  background: linear-gradient(180deg, #ffffff 0%, #fbfdff 100%);
  box-shadow: 0 8px 20px rgba(15, 23, 42, 0.03);
}

.comparison-card-featured {
  border-color: #bfdbfe;
  background: linear-gradient(180deg, #eff6ff 0%, #ffffff 100%);
}

.comparison-card-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.9rem;
}

.comparison-card-head span {
  font-size: 0.9rem;
  font-weight: 700;
  color: #334155;
}

.comparison-card-head strong {
  font-size: 1.55rem;
  line-height: 1;
}

.comparison-values {
  display: grid;
  gap: 0.55rem;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.comparison-values div {
  border-radius: 0.8rem;
  padding: 0.65rem 0.7rem;
  background: #f8fafc;
  border: 1px solid #e5edf7;
}

.comparison-values small {
  display: block;
  color: var(--color-muted);
  margin-bottom: 0.18rem;
  font-size: 0.75rem;
}

.comparison-values b {
  font-size: 0.96rem;
  color: #0f172a;
}

.compare-controls {
  margin-bottom: 0.9rem;
  max-width: 32rem;
}

.comparison-index-files,
.indexing-summary,
.issue-filters {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.comparison-file-card,
.summary-box {
  display: grid;
  gap: 0.22rem;
  min-width: 12rem;
  padding: 0.8rem 0.9rem;
  border-radius: 0.9rem;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
}

.comparison-lists {
  display: grid;
  gap: 0.8rem;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.comparison-list-card {
  border: 1px solid var(--color-border);
  border-radius: 1rem;
  padding: 0.95rem;
  background: #fff;
}

.comparison-list-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.65rem;
  flex-wrap: wrap;
  margin-bottom: 0.8rem;
}

.comparison-list-head h3 {
  margin: 0;
}

.comparison-counter {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 1.9rem;
  padding: 0 0.65rem;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 700;
}

.comparison-counter-warn {
  color: #92400e;
  background: #fef3c7;
}

.comparison-counter-good {
  color: #166534;
  background: #dcfce7;
}

.comparison-issue-list {
  margin: 0;
  padding-left: 1rem;
  display: grid;
  gap: 0.55rem;
}

.comparison-issue-list li {
  display: grid;
  gap: 0.18rem;
}

.comparison-issue-list li strong {
  color: #0f172a;
}

.comparison-issue-list li span {
  color: var(--color-muted);
  word-break: break-word;
  font-size: 0.86rem;
}

.block-hint,
.tech-summary {
  margin: 0 0 0.7rem;
}

.seo-ai-card {
  margin-top: 0.85rem;
  background: linear-gradient(180deg, #f7fbff 0%, #fdfefe 100%);
  border: 1px solid #dbeafe;
  box-shadow: 0 12px 30px rgba(59, 130, 246, 0.05);
  position: relative;
  overflow: hidden;
}

.seo-ai-card::before {
  content: "";
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at top right, rgba(59, 130, 246, 0.08), transparent 24%),
    radial-gradient(circle at left bottom, rgba(147, 197, 253, 0.12), transparent 26%);
  pointer-events: none;
}

.seo-ai-card > * {
  position: relative;
  z-index: 1;
}

.seo-empty-panel {
  padding: 1rem;
  border-radius: 0.95rem;
  background: rgba(255, 255, 255, 0.75);
  border: 1px dashed #bfdbfe;
}

.seo-ai-summary-box {
  padding: 0.95rem 1rem;
  border-radius: 1rem;
  background: rgba(255, 255, 255, 0.78);
  border: 1px solid #dbeafe;
}

.seo-ai-summary {
  margin: 0 0 0.55rem;
  line-height: 1.6;
}

.seo-ai-meta {
  display: flex;
  gap: 0.65rem;
  flex-wrap: wrap;
  margin-bottom: 0.2rem;
}

.seo-meta-chip,
.priority-pill,
.severity-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 700;
  padding: 0.18rem 0.6rem;
}

.seo-meta-chip {
  color: #1e3a8a;
  background: #eaf3ff;
  border: 1px solid #dbeafe;
}

.seo-ai-overview {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
  margin-top: 0.8rem;
  margin-bottom: 0.65rem;
}

.seo-ai-overview-chip {
  display: inline-flex;
  align-items: center;
  border: 1px solid #dbe5f1;
  border-radius: 999px;
  padding: 0.24rem 0.58rem;
  font-size: 0.76rem;
  color: #1e3a8a;
  background: #eff6ff;
}

.seo-ai-section {
  display: grid;
  gap: 0.48rem;
  margin-top: 0.7rem;
}

.seo-ai-section h3 {
  margin: 0;
  font-size: 0.98rem;
  line-height: 1.3;
}

.seo-ai-metrics-grid {
  display: grid;
  gap: 0.6rem;
  grid-template-columns: repeat(auto-fit, minmax(13rem, 1fr));
}

.seo-ai-metric-card,
.seo-ai-problem-item,
.seo-ai-fix-plan li {
  border: 1px solid #dbeafe;
  border-radius: 0.85rem;
  padding: 0.72rem 0.75rem;
  background: rgba(255, 255, 255, 0.82);
}

.seo-ai-metric-head,
.seo-ai-problem-head,
.seo-ai-fix-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.55rem;
  flex-wrap: wrap;
}

.seo-ai-metric-card strong {
  margin-top: 0.35rem;
  display: inline-block;
  font-size: 1.05rem;
}

.seo-ai-metric-card p,
.seo-ai-problem-item p,
.seo-ai-fix-plan p {
  margin: 0.35rem 0 0;
}

.seo-ai-problems {
  display: grid;
  gap: 0.55rem;
}

.seo-ai-fix-plan {
  margin: 0;
  padding-left: 1rem;
  display: grid;
  gap: 0.55rem;
}

.seo-ai-step {
  display: inline-flex;
  align-items: center;
  border: 1px solid #dbe5f1;
  border-radius: 999px;
  padding: 0.14rem 0.5rem;
  font-size: 0.74rem;
  font-weight: 700;
  color: #1d4ed8;
  background: #eff6ff;
}

.seo-ai-list {
  margin: 0;
  padding-left: 1rem;
  display: grid;
  gap: 0.4rem;
}

.seo-ai-error {
  margin-top: 0.5rem;
}

.seo-metric-status-info {
  color: #1e3a8a;
  background: #e0e7ff;
}

.priority-urgent,
.severity-high {
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

.severity-low {
  color: #166534;
  background: #dcfce7;
}

.url-cell {
  max-width: 20rem;
  word-break: break-word;
}

.issue-inline-list {
  font-size: 0.82rem;
  color: var(--color-muted);
  word-break: break-word;
  line-height: 1.45;
}

.issue-filter-btn {
  min-height: 2.1rem;
  border: 1px solid var(--color-border);
  border-radius: 999px;
  padding: 0 0.75rem;
  background: #fff;
  font-weight: 700;
  cursor: pointer;
  color: #050505;
  transition: all 0.18s ease;
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
.seo-score-warn,
.delta-neutral {
  color: #b45309;
}

.status-idle {
  color: #6b7280;
}

.seo-score-bad,
.delta-negative,
.trend-worse {
  color: #b91c1c;
}

.seo-score-good,
.delta-positive,
.trend-better {
  color: #15803d;
}

.trend-stable {
  color: #1e40af;
}

.comparison-trend {
  margin: 0;
  font-weight: 800;
  font-size: 1rem;
}

.comparison-note {
  font-size: 0.84rem;
}

.empty-state {
  margin: 0;
}

.responsive-table-wrap {
  overflow-x: auto;
}

.mobile-stack-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
}

.mobile-stack-table th,
.mobile-stack-table td {
  vertical-align: top;
}

@keyframes seo-spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 1200px) {
  .comparison-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 960px) {
  .seo-anchor-nav-wrap {
    top: 0.35rem;
  }

  .seo-start-row,
  .comparison-grid,
  .comparison-lists {
    grid-template-columns: 1fr;
  }

  .comparison-values {
    grid-template-columns: 1fr 1fr 1fr;
  }

  .indexing-summary {
    flex-direction: column;
    gap: 0.45rem;
  }
}

@media (max-width: 768px) {
  .card-head-wrap {
    align-items: stretch;
  }

  .seo-export-btn,
  .seo-compare-btn,
  .seo-ai-refresh-btn,
  .seo-start-btn,
  .seo-stop-btn {
    width: 100%;
  }

  .seo-start-row {
    grid-template-columns: 1fr;
  }

  .seo-anchor-nav {
    padding: 0.45rem;
    border-radius: 0.85rem;
  }

  .seo-anchor-nav-btn {
    min-height: 2rem;
    font-size: 0.76rem;
  }

  .comparison-values {
    grid-template-columns: 1fr;
  }

  .comparison-file-card,
  .summary-box {
    width: 100%;
    min-width: 0;
  }

  .mobile-stack-table thead {
    display: none;
  }

  .mobile-stack-table,
  .mobile-stack-table tbody,
  .mobile-stack-table tr,
  .mobile-stack-table td {
    display: block;
    width: 100%;
  }

  .mobile-stack-table tbody {
    display: grid;
    gap: 0.8rem;
  }

  .mobile-stack-table tr {
    border: 1px solid #e5edf7;
    border-radius: 0.95rem;
    background: #fff;
    padding: 0.6rem 0.7rem;
    box-shadow: 0 8px 18px rgba(15, 23, 42, 0.03);
  }

  .mobile-stack-table td {
    border: none;
    padding: 0.46rem 0;
    text-align: left;
  }

  .mobile-stack-table td::before {
    content: attr(data-label);
    display: block;
    margin-bottom: 0.18rem;
    font-size: 0.74rem;
    font-weight: 700;
    color: #64748b;
  }

  .mobile-stack-table td[colspan] {
    text-align: left;
  }

  .mobile-stack-table td[colspan]::before {
    display: none;
  }

  .url-cell {
    max-width: 100%;
  }

  .seo-ai-metrics-grid {
    grid-template-columns: 1fr;
  }

  .seo-ai-problem-head,
  .seo-ai-fix-head,
  .seo-ai-metric-head,
  .comparison-list-head {
    align-items: flex-start;
  }
}
</style>