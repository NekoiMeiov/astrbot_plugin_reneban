/**
 * ReNeBan · Dashboard Page
 *
 * Vanilla ES module. Talks to the plugin backend exclusively through the
 * AstrBot plugin Page bridge, so the iframe stays inside its sandbox.
 * No build step and no external dependency: it runs on an offline instance.
 */

/* ------------------------------------------------------------------ *
 * bridge
 * ------------------------------------------------------------------ */

const bridge = window.AstrBotPluginPage;

const DEFAULT_CONTEXT = {
  pluginName: "astrbot_plugin_reneban",
  pageName: "reneban",
  locale: "zh-CN",
  i18n: {},
  isDark: false,
};

/** Chinese source strings; `bridge.t()` can override every one of them. */
const FALLBACK = {
  eyebrow: "ReNeBan 控制台",
  heading: "黑名单管理面板",
  subtitle: "统一查看与维护会话级、全局级的禁用与解限记录",
  refresh: "刷新",
  loading: "正在读取黑名单数据…",
  loadFailed: "读取数据失败",
  retry: "重试",
  empty: "暂无数据",
  emptyHint: "当前没有被禁用的用户或会话",
  emptySearch: "没有匹配的记录",
  noReason: "无理由",
  permanent: "永久",
  expired: "已过期",
  search: "搜索用户 ID、会话或理由",
  filterScope: "范围",
  filterKind: "类型",
  filterState: "时限",
  sortBy: "排序",
  scopeAll: "全部范围",
  scopeSession: "会话",
  scopeGlobal: "全局",
  kindAll: "全部类型",
  kindBan: "禁用",
  kindPass: "解限",
  stateAll: "全部时限",
  statePermanent: "永久",
  stateTemporary: "限时",
  stateExpiring: "24 小时内到期",
  sortExpiring: "即将到期优先",
  sortLatest: "最新添加优先",
  sortId: "按 ID 排序",
  unitRecords: "条记录",
  colTarget: "对象",
  colScope: "范围",
  colKind: "类型",
  colRemaining: "剩余时长",
  colExpireAt: "到期时间",
  colReason: "理由",
  colActions: "操作",
  actionPass: "解限",
  actionBan: "禁用",
  actionExtend: "延长",
  actionReduce: "缩短",
  actionDelete: "删除",
  actionResetUser: "清除用户",
  actionResetSession: "清除会话",
  actionCopyUmo: "复制 UMO",
  copied: "已复制",
  cancel: "取消",
  confirm: "确认",
  close: "关闭",
  detail: "记录详情",
  layoutCards: "卡片",
  layoutTable: "表格",
  enableOn: "禁用功能已启用",
  enableOff: "禁用功能已停用",
  enableHint: "与 /ban-enable、/ban-disable 相同，重启后恢复配置值",
  enableAction: "启用功能",
  disableAction: "停用功能",
  confirmEnableTitle: "启用禁用功能？",
  confirmEnableBody: "启用后，黑名单立即生效：名单内的用户将无法再让机器人响应。",
  confirmDisableTitle: "停用禁用功能？",
  confirmDisableBody: "停用后，黑名单立即失效：名单内的用户将恢复使用，但记录会保留。",
  enableConfirmNote: "与 /ban-enable、/ban-disable 效果相同，重启后恢复配置文件中的值。",
  statTotal: "记录总数",
  statBans: "禁用记录",
  statPasses: "解限记录",
  statPermanent: "永久记录",
  statExpiring: "24 小时内到期",
  statSessions: "涉及会话",
  tabOverview: "总览",
  tabGlobal: "全局记录",
  tabSession: "会话记录",
  tabSessionLevel: "会话级记录",
  tabSessions: "会话列表",
  sessionsTitle: "涉及会话",
  sessionBans: "禁用",
  sessionPasses: "解限",
  timelineTitle: "即将到期",
  timelineEmpty: "没有即将到期的记录",
  timelineHint: "按到期时间排序，最多显示 8 条",
  dialogBanTitle: "新增禁用记录",
  dialogPassTitle: "新增解限记录",
  dialogExtendTitle: "延长剩余时长",
  dialogReduceTitle: "缩短剩余时长",
  dialogDeleteTitle: "删除记录",
  dialogResetUserTitle: "清除用户全部记录",
  dialogResetSessionTitle: "清除会话全部记录",
  fieldTarget: "对象",
  fieldTargetUser: "用户",
  fieldTargetSession: "整个会话",
  fieldScope: "作用范围",
  fieldId: "用户 ID",
  fieldUmo: "会话 UMO",
  fieldDuration: "时长",
  fieldReason: "理由",
  fieldDelta: "调整幅度",
  durationHint: "格式：1d2h30m（d 天 / h 小时 / m 分钟 / s 秒），留空或 0 表示永久",
  reasonHint: "留空表示无理由",
  deltaHint: "单位：秒，正数延长，负数缩短",
  viewToggle: "视图切换",
  tabsLabel: "记录分类",
  statsLabel: "统计",
  durationPreset: "常用时长",
  preset1h: "1 小时",
  preset1d: "1 天",
  preset7d: "7 天",
  preset30d: "30 天",
  presetForever: "永久",
  confirmDelete: "确定要删除这条记录吗？此操作不可撤销。",
  confirmResetUser: "将清除该用户在会话与全局下的全部禁用/解限记录，确定继续吗？",
  confirmResetSession: "将清除该会话的全部记录，确定继续吗？",
  opSuccess: "操作成功",
  opFailed: "操作失败",
  fieldRequired: "请先填写必填项",
  sessionIdLabel: "会话",
  platformLabel: "平台",
  msgTypeLabel: "消息类型",
  selectSession: "选择会话",
  shortcuts: "快捷键：R 刷新 · / 搜索 · Esc 关闭弹窗",
  create: "新增记录",
  statPermanentHint: "无到期时间",
  statExpiringHint: "24 小时内自动清理",
  statSessionsHint: "有记录的会话",
  histTitle: "到期分布",
  histHint: "按剩余时长分桶，永久记录不计入",
  mixTitle: "禁用 / 解限构成",
  mixHint: "仅统计用户级记录",
  mixBans: "禁用",
  mixPasses: "解限",
  mixPermanent: "永久记录",
  mixTemporary: "限时记录",
  bucketLt1h: "≤1 小时",
  bucketLt6h: "1–6 小时",
  bucketLt24h: "6–24 小时",
  bucketLt3d: "1–3 天",
  bucketLt7d: "3–7 天",
  bucketGt7d: ">7 天",
  insightTitle: "洞察",
  insightNextExpiry: "最近到期",
  insightTopUser: "记录最多的用户",
  insightTopSession: "限制最多的会话",
  heatTitle: "未来 7 天到期热力",
  heatHint: "每格 3 小时，颜色越深到期越集中",
  heatToday: "今天",
  heatAxisHint: "列＝日期，行＝当天时段",
  heatLess: "少",
  heatMore: "多",
};

const ICON = {
  ban: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="9"/><path d="M5.6 5.6l12.8 12.8" stroke-linecap="round"/></svg>',
  pass: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="9"/><path d="M8 12.5l2.8 2.7L16 9.5" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  globe: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><circle cx="12" cy="12" r="9"/><path d="M3.5 9h17M3.5 15h17M12 3a15 15 0 010 18M12 3a15 15 0 000 18"/></svg>',
  chat: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M20 12a8 8 0 01-11.6 7.1L4 20l1-4.2A8 8 0 1120 12z" stroke-linejoin="round"/></svg>',
  clock: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="9"/><path d="M12 7.5V12l3 2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  timer: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><circle cx="12" cy="13.5" r="7.5"/><path d="M12 10v3.8l2.4 1.6M9 3h6" stroke-linecap="round"/></svg>',
  infinity: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M7 9c-2 0-3.2 1.3-3.2 3S5 15 7 15c2.6 0 3.4-6 6-6 2 0 3.2 1.3 3.2 3S15 15 13 15c-2.6 0-3.4-6-6-6z" stroke-linecap="round"/></svg>',
  users: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><circle cx="9" cy="8" r="3.4"/><path d="M3.5 19.5c0-3 2.5-5 5.5-5s5.5 2 5.5 5" stroke-linecap="round"/><path d="M16 5.6a3.4 3.4 0 010 5.6M17.5 14.8c2 .6 3.3 2.3 3.3 4.7" stroke-linecap="round"/></svg>',
  pie: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M12 3.5a8.5 8.5 0 108.5 8.5H12z" stroke-linejoin="round"/><path d="M14.5 3.9A8.5 8.5 0 0120.1 9.5h-5.6z" stroke-linejoin="round"/></svg>',
  spark: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M12 3.5l1.9 4.9 4.9 1.9-4.9 1.9L12 17.1l-1.9-4.9L5.2 10.3l4.9-1.9z" stroke-linejoin="round"/><path d="M18.5 16.5l.8 2 2 .8-2 .8-.8 2-.8-2-2-.8 2-.8z" stroke-linejoin="round"/></svg>',
  heat: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="3.5" y="4" width="4" height="4" rx="1.2"/><rect x="10" y="4" width="4" height="4" rx="1.2"/><rect x="16.5" y="4" width="4" height="4" rx="1.2"/><rect x="3.5" y="10" width="4" height="4" rx="1.2"/><rect x="10" y="10" width="4" height="4" rx="1.2"/><rect x="16.5" y="10" width="4" height="4" rx="1.2"/><rect x="3.5" y="16" width="4" height="4" rx="1.2"/><rect x="10" y="16" width="4" height="4" rx="1.2"/><rect x="16.5" y="16" width="4" height="4" rx="1.2"/></svg>',
  empty: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M4 8.5l4-4.5h8l4 4.5V18a2 2 0 01-2 2H6a2 2 0 01-2-2z" stroke-linejoin="round"/><path d="M4 13h4l1.2 2h5.6L16 13h4" stroke-linejoin="round"/></svg>',
  search: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="11" cy="11" r="7"/><path d="M16.5 16.5L21 21" stroke-linecap="round"/></svg>',
  warn: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M10.3 3.9L2.6 17.2A2 2 0 004.3 20.2h15.4a2 2 0 001.7-3L13.7 3.9a2 2 0 00-3.4 0z" stroke-linejoin="round"/><path d="M12 9v4" stroke-linecap="round"/><circle cx="12" cy="16.6" r=".9" fill="currentColor" stroke="none"/></svg>',
  info: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><circle cx="12" cy="12" r="9"/><path d="M12 11v5.5" stroke-linecap="round"/><circle cx="12" cy="7.8" r=".95" fill="currentColor" stroke="none"/></svg>',
  alert: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><circle cx="12" cy="12" r="9"/><path d="M12 7.5v5.5" stroke-linecap="round"/><circle cx="12" cy="16.3" r=".95" fill="currentColor" stroke="none"/></svg>',
  ok: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12.5l4.5 4.5L19 7.5" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  plus: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9"><path d="M12 5v14M5 12h14" stroke-linecap="round"/></svg>',
  minus: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9"><path d="M5 12h14" stroke-linecap="round"/></svg>',
  trash: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M5 7h14M10 7V5h4v2M6.5 7l.8 12.1A1.5 1.5 0 008.8 20.5h6.4a1.5 1.5 0 001.5-1.4L17.5 7" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  copy: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="9" y="9" width="11" height="11" rx="2.2"/><path d="M15 6.5V5.8A1.8 1.8 0 0013.2 4H5.8A1.8 1.8 0 004 5.8v7.4A1.8 1.8 0 005.8 15h.7" stroke-linecap="round"/></svg>',
  broom: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M14.5 3.5l-4 4M17 6l-9 9M4.5 19.5c2.5.6 5-.5 6.4-2.4l1.9-2.5-3.4-3.4-2.5 1.9c-1.9 1.4-3 3.9-2.4 6.4z" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  refresh: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M20 11a8 8 0 10-2.3 5.7" stroke-linecap="round"/><path d="M20 4v7h-7" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  close: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9"><path d="M6 6l12 12M18 6L6 18" stroke-linecap="round"/></svg>',
  rows: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 6h16M4 12h16M4 18h16" stroke-linecap="round"/></svg>',
  grid: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="4" y="4" width="7" height="7" rx="2"/><rect x="13" y="4" width="7" height="7" rx="2"/><rect x="4" y="13" width="7" height="7" rx="2"/><rect x="13" y="13" width="7" height="7" rx="2"/></svg>',
  shield:
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M12 3l7.5 2.6v5.6c0 4.4-3 8.1-7.5 9.2-4.5-1.1-7.5-4.8-7.5-9.2V5.6z" stroke-linejoin="round"/><path d="M8.8 12.1l2.4 2.3 4.1-4.4" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  hourglass:
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M7 3.5h10M7 20.5h10M8.5 3.5v3.2c0 2 3.5 3.4 3.5 5.3s-3.5 3.3-3.5 5.3v3.2M15.5 3.5v3.2c0 2-3.5 3.4-3.5 5.3s3.5 3.3 3.5 5.3v3.2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  layers:
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M12 3.5l8.5 4.6-8.5 4.6-8.5-4.6z" stroke-linejoin="round"/><path d="M4.5 12.4L12 16.5l7.5-4.1M4.5 16.2L12 20.3l7.5-4.1" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  crown:
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M4 17.5h16M4.5 7l3.2 3.4L12 5.2l4.3 5.2L19.5 7l-1.3 8.2H5.8z" stroke-linecap="round" stroke-linejoin="round"/></svg>',
};

/* ------------------------------------------------------------------ *
 * helpers
 * ------------------------------------------------------------------ */

const $ = (id) => document.getElementById(id);

const t = (key, fallback) => {
  const text = bridge?.t?.(`pages.reneban.${key}`, undefined);
  return text || fallback || FALLBACK[key] || key;
};

/** Locale reported to the backend, so failures come back in the same language. */
const currentLocale = () =>
  bridge?.getLocale?.() || bridge?.getContext?.()?.locale || "zh-CN";

const escapeHtml = (value) =>
  String(value ?? "").replace(
    /[&<>"']/g,
    (char) =>
      ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;",
      })[char],
  );

const clamp = (value, min, max) => Math.min(Math.max(value, min), max);

/** Width reference used by the countdown bars: 30 days. */
const BAR_REFERENCE = 30 * 86400;

/** Compact, locale-free duration: `1d 2h`, `3h 05m`, `42s`. */
function formatDuration(seconds) {
  const total = Math.max(0, Math.floor(seconds));
  const days = Math.floor(total / 86400);
  const hours = Math.floor((total % 86400) / 3600);
  const minutes = Math.floor((total % 3600) / 60);
  const secs = total % 60;

  if (days > 0) return `${days}d ${hours}h`;
  if (hours > 0) return `${hours}h ${String(minutes).padStart(2, "0")}m`;
  if (minutes > 0) return `${minutes}m ${String(secs).padStart(2, "0")}s`;
  return `${secs}s`;
}

/** `1d2h30m0s` → seconds. Returns `null` when the expression is invalid. */
function parseDurationToSeconds(text, now) {
  const raw = String(text ?? "").trim();
  if (!raw || raw === "0") return 0;
  const match = /^(?=.*\d)(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s?)?$/.exec(raw);
  if (!match) return null;
  const [, d, h, m, s] = match;
  const total =
    Number(d || 0) * 86400 +
    Number(h || 0) * 3600 +
    Number(m || 0) * 60 +
    Number(s || 0);
  return Number.isFinite(total) ? total : null;
}

/** Seconds → the expression understood by the chat commands. */
function secondsToDurationText(seconds) {
  let rest = Math.max(0, Math.floor(seconds));
  if (rest === 0) return "0";
  const parts = [];
  for (const [unit, size] of [
    ["d", 86400],
    ["h", 3600],
    ["m", 60],
    ["s", 1],
  ]) {
    const amount = Math.floor(rest / size);
    if (amount > 0) {
      parts.push(`${amount}${unit}`);
      rest -= amount * size;
    }
  }
  return parts.join("");
}

const formatDateTime = (timestamp) =>
  new Date(timestamp * 1000).toLocaleString(undefined, {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });

/** Short calendar date, used where a duration alone is ambiguous. */
const formatDate = (timestamp) =>
  new Date(timestamp * 1000).toLocaleDateString(undefined, {
    month: "2-digit",
    day: "2-digit",
  });

const initials = (text) => {
  const clean = String(text ?? "").replace(/[^\p{L}\p{N}]/gu, "");
  if (!clean) return "??";
  return clean.length <= 2 ? clean.toUpperCase() : clean.slice(-2).toUpperCase();
};

/** Map a message type to a short platform badge label. */
const prettyMessageType = (value) =>
  ({ GroupMessage: "群聊", FriendMessage: "私聊", GuildMessage: "频道" })[value] ||
  value ||
  "—";

const matchesSearch = (record, needle) => {
  if (!needle) return true;
  const haystack = [
    record.id,
    record.umo,
    record.session_id,
    record.session_name,
    record.reason,
    record.platform,
    record.message_type,
  ]
    .filter(Boolean)
    .join(" ")
    .toLowerCase();
  return haystack.includes(needle);
};

/** Fill every `data-icon="name"` placeholder with its inline SVG. */
function hydrateIcons(root = document) {
  root.querySelectorAll("[data-icon]").forEach((node) => {
    const markup = ICON[node.dataset.icon];
    if (markup) node.innerHTML = markup;
  });
}

/** Clamp a 0..1 ratio into a usable bar width. */
const ratioToWidth = (ratio) =>
  `${(clamp(Number.isFinite(ratio) ? ratio : 0, 0, 1) * 100).toFixed(1)}%`;

/** Geometry of the metric rings: r=17 inside a 38x38 viewBox. */
const RING_RADIUS = 17;
const RING_CIRCUMFERENCE = 2 * Math.PI * RING_RADIUS;

/**
 * Animate every `[data-countup]` value to its target. One animation per node:
 * a repeat render of an unchanged value is left alone, and an interrupted
 * animation resumes towards the new target instead of snapping back to zero.
 */
const countUpState = new WeakMap();

function runCountUps() {
  const nodes = document.querySelectorAll("[data-countup]");
  if (nodes.length === 0) return;
  const reduceMotion = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;

  nodes.forEach((node) => {
    const target = Number(node.dataset.countup) || 0;
    const previous = countUpState.get(node);
    if (previous && previous.target === target && previous.done) return;
    if (reduceMotion) {
      countUpState.set(node, { target, done: true });
      node.textContent = String(target);
      return;
    }

    const from = previous ? previous.current : 0;
    const started = performance.now();
    const duration = 520;
    const state = { target, current: from, done: false };
    countUpState.set(node, state);

    const step = (now) => {
      const elapsed = Number.isFinite(now) ? Math.max(0, now - started) : duration;
      // Clamped on both ends: a non-monotonic or NaN timestamp must never
      // produce a negative reading such as "-1".
      const progress = clamp(elapsed / duration, 0, 1);
      const eased = 1 - (1 - progress) ** 3;
      const shown = Math.round(from + (target - from) * eased);
      const bound = Math.max(from, target);
      state.current = clamp(shown, 0, bound);
      node.textContent = String(state.current);
      if (progress < 1) {
        requestAnimationFrame(step);
      } else {
        state.current = target;
        state.done = true;
        node.textContent = String(target);
      }
    };
    requestAnimationFrame(step);
  });
}

/** How many records expire in each slot of the next `days` days.
 *
 * The strip is a 7-column grid and CSS places cells column by column, so the
 * array is filled column-major: one column per day, one cell per `hours` slot
 * within that day.
 */
function expiryHeat(days, hours) {
  const now = Date.now() / 1000;
  const rows = Math.round(24 / hours);
  const cells = Array.from({ length: days * rows }, () => ({
    key: null,
    offset: Number.POSITIVE_INFINITY,
    bans: 0,
    passes: 0,
  }));

  for (const record of [...state.records, ...state.sessionRecords]) {
    if (record.time === 0) continue;
    const delta = record.time - now;
    if (delta <= 0) continue;
    const day = Math.floor(delta / 86400);
    if (day >= days) continue;
    const slot = Math.floor((delta % 86400) / (hours * 3600));
    const cell = cells[day * rows + slot];
    if (record.kind === "ban") cell.bans += 1;
    else cell.passes += 1;
    // A cell can hold several records; keep the soonest so the tooltip and the
    // click target stay meaningful.
    if (delta < cell.offset) {
      cell.offset = delta;
      cell.key = recordKey(record);
    }
  }
  return cells;
}

/* ------------------------------------------------------------------ *
 * state
 * ------------------------------------------------------------------ */

const state = {
  loading: true,
  error: null,
  enabled: false,
  records: [],
  sessionRecords: [],
  sessions: [],
  stats: {},
  buckets: [],
  insights: {},
  tab: "overview",
  filters: { scope: "all", kind: "all", state: "all", sort: "expiring" },
  search: "",
  layout: "table",
  sort: { key: "remaining", dir: "asc" },
  modal: null,
  /** Page scroll offset held while a dialog is open, 0 when none is. */
  pageScrollY: 0,
  busy: false,
};

const applyTheme = (isDark) => {
  document.documentElement.setAttribute(
    "data-theme",
    isDark ? "dark" : "light",
  );
};

/* ------------------------------------------------------------------ *
 * data access
 * ------------------------------------------------------------------ */

async function loadData() {
  const payload = await bridge.apiGet("overview", { locale: currentLocale() });
  state.enabled = Boolean(payload?.enabled);
  state.records = Array.isArray(payload?.records) ? payload.records : [];
  state.sessionRecords = Array.isArray(payload?.session_records)
    ? payload.session_records
    : [];
  state.sessions = Array.isArray(payload?.sessions) ? payload.sessions : [];
  state.stats = payload?.stats || {};
  state.buckets = Array.isArray(payload?.expiry_buckets)
    ? payload.expiry_buckets
    : [];
  state.insights = payload?.insights || {};
}

async function refresh({ silent = false } = {}) {
  if (state.busy) return;
  state.busy = true;
  if (!silent) state.error = null;
  try {
    await loadData();
    state.error = null;
    showApp();
    render();
  } catch (error) {
    state.error = error?.message || String(error);
    if (state.records.length === 0 && state.error) showFatal(state.error);
    else render();
    if (silent) toast("err", t("opFailed"), state.error);
  } finally {
    state.busy = false;
  }
}

/** Run a write call, then refresh; surfaces bridge errors as toasts. */
async function mutate(endpoint, body, successMessage) {
  if (state.busy) return false;
  state.busy = true;
  try {
    // The locale travels with the request so validation errors come back in
    // the language the operator is reading.
    await bridge.apiPost(endpoint, { ...body, locale: currentLocale() });
    await loadData();
    render();
    toast("ok", successMessage || t("opSuccess"));
    return true;
  } catch (error) {
    toast("err", t("opFailed"), error?.message || String(error));
    return false;
  } finally {
    state.busy = false;
  }
}

/* ------------------------------------------------------------------ *
 * filtering
 * ------------------------------------------------------------------ */

function currentRecords() {
  const { scope, kind, state: stateFilter, sort } = state.filters;
  const mode =
    state.tab === "global"
      ? "global"
      : state.tab === "session"
        ? "session"
        : state.tab === "sessionLevel"
          ? "sessionLevel"
          : "all";

  let rows =
    mode === "sessionLevel" ? state.sessionRecords.slice() : state.records.slice();
  if (mode === "global") rows = rows.filter((item) => item.scope === "global");
  if (mode === "session") rows = rows.filter((item) => item.scope === "session");

  const needle = state.search.trim().toLowerCase();
  rows = rows.filter((item) => {
    if (!matchesSearch(item, needle)) return false;
    if (mode === "all") {
      if (scope !== "all" && item.scope !== scope) return false;
      if (kind !== "all" && item.kind !== kind) return false;
    }
    if (stateFilter === "permanent" && item.time !== 0) return false;
    if (stateFilter === "temporary" && item.time === 0) return false;
    if (
      stateFilter === "expiring" &&
      !(item.time !== 0 && item.remaining > 0 && item.remaining <= 86400)
    ) {
      return false;
    }
    return true;
  });

  const byRemainingAsc = (a, b) => {
    if (a.time === 0 && b.time === 0) return a.id.localeCompare(b.id);
    if (a.time === 0) return 1;
    if (b.time === 0) return -1;
    return a.time - b.time;
  };

  if (sort === "expiring") rows.sort(byRemainingAsc);
  else if (sort === "latest") rows.sort((a, b) => b.time - a.time);
  else rows.sort((a, b) => a.id.localeCompare(b.id, undefined, { numeric: true }));

  return rows;
}

/* ------------------------------------------------------------------ *
 * rendering
 * ------------------------------------------------------------------ */

function showApp() {
  $("boot").hidden = true;
  $("app").hidden = false;
  $("fatal").hidden = true;
  hydrateIcons($("app"));
}

function showFatal(message) {
  $("boot").hidden = true;
  $("app").hidden = true;
  $("fatal").hidden = false;
  $("fatalTitle").textContent = t("loadFailed");
  $("fatalMsg").textContent = message;
  $("fatalRetry").textContent = t("retry");
}

function renderStaticStrings() {
  // Only strings that live in the static shell. Everything inside a rendered
  // region is set by its own render function.
  $("eyebrow").textContent = t("eyebrow");
  $("heading").textContent = t("heading");
  $("refreshLabel").textContent = t("refresh");
  $("createLabel").textContent = t("create");
  $("searchInput").placeholder = t("search");
  $("footerHint").textContent = t("shortcuts");
  $("layoutTableLabel").textContent = t("layoutTable");
  $("layoutCardsLabel").textContent = t("layoutCards");
  // The shell ships a readable default so the first paint is never empty; these
  // keep the non-visible labels in step with the active language.
  document.title = t("heading");
  $("refreshBtn").title = t("refresh");
  $("searchInput").setAttribute("aria-label", t("search"));
  $("stats").setAttribute("aria-label", t("statsLabel"));
  $("heat").setAttribute("aria-label", t("heatTitle"));
  $("tabs").setAttribute("aria-label", t("tabsLabel"));
  $("modalClose").setAttribute("aria-label", t("close"));
  const viewGroup = document.querySelector(".viewtoggle .segmented");
  if (viewGroup) viewGroup.setAttribute("aria-label", t("viewToggle"));
}

function render() {
  renderStaticStrings();
  renderEnableSwitch();
  renderStats();
  renderFilterOptions();
  renderTabs();
  renderBento();
  renderContent();
  $("footerMeta").textContent = `${state.stats.total ?? 0} ${t("unitRecords")}`;
}

function renderEnableSwitch() {
  const node = $("enableSwitch");
  node.setAttribute("aria-checked", state.enabled ? "true" : "false");
  node.title = t("enableHint");
  $("enableLabel").textContent = state.enabled ? t("enableOn") : t("enableOff");
}

function statCard({ label, value, hint, icon, tone, ratio, pctLabel }) {
  const share = clamp(Number.isFinite(ratio) ? ratio : 0, 0, 1);
  const circumference = RING_CIRCUMFERENCE;
  // Below ~8% the arc is a smudge, so the track is shown on its own.
  const showArc = share >= 0.08 || share === 0;
  return `
    <article class="stat ${tone ? `stat--${tone}` : ""}">
      <p class="stat__label">${ICON[icon] || ""}<span>${escapeHtml(label)}</span></p>
      <div class="stat__row">
        <p class="stat__value num" data-countup="${escapeHtml(String(value ?? 0))}">0</p>
        <span class="ring" role="img" aria-label="${escapeHtml(`${label} ${pctLabel ?? ""}`.trim())}">
          <svg viewBox="0 0 38 38">
            <circle class="ring__track" cx="19" cy="19" r="${RING_RADIUS}"></circle>
            ${
              showArc
                ? `<circle class="ring__value" cx="19" cy="19" r="${RING_RADIUS}"
                     stroke-dasharray="${(share * circumference).toFixed(1)} ${circumference}"
                     style="--dash:${(share * circumference).toFixed(1)}"></circle>`
                : ""
            }
          </svg>
          <span class="ring__pct">${pctLabel || ""}</span>
        </span>
      </div>
      ${hint ? `<p class="stat__hint">${escapeHtml(hint)}</p>` : ""}
    </article>`;
}

function renderStats() {
  const stats = state.stats || {};
  const total = Number(stats.total) || 0;
  const share = (value) => (total > 0 ? (Number(value) || 0) / total : 0);
  const percent = (value) => (total > 0 ? `${Math.round((value / total) * 100)}%` : "0%");
  const temporary = Number(stats.temporary) || 0;
  const sessions = Number(stats.sessions) || 0;
  const sessionRecords = state.sessionRecords.length;
  const activeSessions = state.sessions.filter(
    (session) => session.bans + session.passes > 0,
  ).length;

  $("stats").innerHTML = [
    statCard({
      label: t("statTotal"),
      value: stats.total,
      // The overview tab also lists whole-session records, so spell out the
      // breakdown instead of letting the two totals look inconsistent.
      hint:
        sessionRecords > 0
          ? `${temporary} ${t("stateTemporary")} · +${sessionRecords} ${t("tabSessionLevel")}`
          : `${temporary} ${t("stateTemporary")}`,
      icon: "users",
      ratio: total > 0 ? 1 : 0,
      pctLabel: total > 0 ? "100%" : "0%",
    }),
    statCard({
      label: t("statBans"),
      value: stats.bans,
      icon: "ban",
      tone: "ban",
      ratio: share(stats.bans),
      pctLabel: percent(Number(stats.bans) || 0),
    }),
    statCard({
      label: t("statPasses"),
      value: stats.passes,
      icon: "pass",
      tone: "pass",
      ratio: share(stats.passes),
      pctLabel: percent(Number(stats.passes) || 0),
    }),
    statCard({
      label: t("statPermanent"),
      value: stats.permanent,
      hint: t("statPermanentHint"),
      icon: "infinity",
      tone: "info",
      ratio: share(stats.permanent),
      pctLabel: percent(Number(stats.permanent) || 0),
    }),
    statCard({
      label: t("statExpiring"),
      value: stats.expiring_soon,
      hint: t("statExpiringHint"),
      icon: "hourglass",
      tone: "warn",
      ratio: temporary > 0 ? (Number(stats.expiring_soon) || 0) / temporary : 0,
      pctLabel:
        temporary > 0
          ? `${Math.round(((Number(stats.expiring_soon) || 0) / temporary) * 100)}%`
          : "0%",
    }),
    statCard({
      label: t("statSessions"),
      value: stats.sessions,
      hint: t("statSessionsHint"),
      icon: "chat",
      ratio: sessions > 0 ? activeSessions / sessions : 0,
      pctLabel:
        sessions > 0 ? `${Math.round((activeSessions / sessions) * 100)}%` : "0%",
    }),
  ].join("");
  runCountUps();
}

function option(value, label, selected) {
  return `<option value="${escapeHtml(value)}"${selected ? " selected" : ""}>${escapeHtml(label)}</option>`;
}

function selectGroup(label, id, options) {
  return `
    <label class="select-group">
      <span class="select-group__label">${escapeHtml(label)}</span>
      <select class="select" id="${id}">${options}</select>
    </label>`;
}

function renderFilterOptions() {
  const { filters } = state;
  $("selects").innerHTML = [
    selectGroup(
      t("filterScope"),
      "scopeFilter",
      [
        option("all", t("scopeAll"), filters.scope === "all"),
        option("session", t("scopeSession"), filters.scope === "session"),
        option("global", t("scopeGlobal"), filters.scope === "global"),
      ].join(""),
    ),
    selectGroup(
      t("filterKind"),
      "kindFilter",
      [
        option("all", t("kindAll"), filters.kind === "all"),
        option("ban", t("kindBan"), filters.kind === "ban"),
        option("pass", t("kindPass"), filters.kind === "pass"),
      ].join(""),
    ),
    selectGroup(
      t("filterState"),
      "stateFilter",
      [
        option("all", t("stateAll"), filters.state === "all"),
        option("permanent", t("statePermanent"), filters.state === "permanent"),
        option("temporary", t("stateTemporary"), filters.state === "temporary"),
        option("expiring", t("stateExpiring"), filters.state === "expiring"),
      ].join(""),
    ),
    selectGroup(
      t("sortBy"),
      "sortSelect",
      [
        option("expiring", t("sortExpiring"), filters.sort === "expiring"),
        option("latest", t("sortLatest"), filters.sort === "latest"),
        option("id", t("sortId"), filters.sort === "id"),
      ].join(""),
    ),
  ].join("");

  // Rebuilt every render, so re-attach the listeners here instead of in wire().
  $("scopeFilter").addEventListener("change", (event) => {
    state.filters.scope = event.target.value;
    renderContent();
  });
  $("kindFilter").addEventListener("change", (event) => {
    state.filters.kind = event.target.value;
    renderContent();
  });
  $("stateFilter").addEventListener("change", (event) => {
    state.filters.state = event.target.value;
    renderContent();
  });
  $("sortSelect").addEventListener("change", (event) => {
    state.filters.sort = event.target.value;
    renderContent();
  });

  // The dedicated tabs already pin the scope, so the dropdown is redundant
  // there and would contradict the pinned value.
  $("scopeFilter").disabled = state.tab === "global" || state.tab === "session";

  // The view switch uses the shared segmented control styling.
  document.querySelectorAll("[data-layout]").forEach((btn) => {
    btn.classList.toggle("is-active", btn.dataset.layout === state.layout);
  });
}

function tabCount(id) {
  const records = state.records;
  if (id === "global") return records.filter((item) => item.scope === "global").length;
  if (id === "session") return records.filter((item) => item.scope === "session").length;
  if (id === "sessionLevel") return state.sessionRecords.length;
  if (id === "sessions") return state.sessions.length;
  return records.length + state.sessionRecords.length;
}

function renderTabs() {
  const tabs = [
    ["overview", t("tabOverview")],
    ["global", t("tabGlobal")],
    ["session", t("tabSession")],
    ["sessionLevel", t("tabSessionLevel")],
    ["sessions", t("tabSessions")],
  ];
  $("tabs").innerHTML = tabs
    .map(
      ([id, label]) => `
      <button class="tab${state.tab === id ? " is-active" : ""}" data-tab="${id}" role="tab"
        aria-selected="${state.tab === id}" type="button">
        <span>${escapeHtml(label)}</span>
        <span class="tab__count">${tabCount(id)}</span>
      </button>`,
    )
    .join("");
}

function identityCell(record) {
  const classes = ["avatar"];
  if (record.target === "session") classes.push("avatar--session");
  else if (record.kind === "pass") classes.push("avatar--pass");
  const title = record.id;
  const sub =
    record.scope === "global"
      ? t("scopeGlobal")
      : `${record.session_name || record.session_id} · ${prettyMessageType(record.message_type)}`;
  return `
    <div class="identity">
      <span class="${classes.join(" ")}">${escapeHtml(initials(title))}</span>
      <div class="identity__main">
        <div class="identity__id" title="${escapeHtml(title)}">${escapeHtml(title)}</div>
        <div class="identity__sub" title="${escapeHtml(sub)}">${escapeHtml(sub)}</div>
      </div>
    </div>`;
}

function kindBadge(record) {
  const label = record.kind === "ban" ? t("kindBan") : t("kindPass");
  const icon = record.kind === "ban" ? ICON.ban : ICON.pass;
  return `<span class="badge badge--${record.kind}">${icon}${escapeHtml(label)}</span>`;
}

function scopeBadge(record) {
  if (record.scope === "global") {
    return `<span class="badge badge--global">${ICON.globe}${escapeHtml(t("scopeGlobal"))}</span>`;
  }
  return `<span class="badge">${ICON.chat}${escapeHtml(t("scopeSession"))}</span>`;
}

/** Colour tier for a record's remaining lifetime.
 *
 * `critical` is the single warm state in the whole page, so it has to mean
 * "about to lapse" and nothing else.
 */
function urgencyLevel(record) {
  if (record.time === 0) return "permanent";
  const remaining = Math.max(0, record.remaining);
  if (remaining <= 3600) return "critical";
  if (remaining <= 86400) return "warn";
  return "calm";
}

function countdownCell(record) {
  const permanent = record.time === 0;
  const remaining = Math.max(0, record.remaining);
  const expired = !permanent && remaining <= 0;
  const ratio = permanent ? 1 : clamp(remaining / BAR_REFERENCE, 0.015, 1);
  const level = urgencyLevel(record);

  const text = permanent
    ? t("permanent")
    : expired
      ? t("expired")
      : formatDuration(remaining);
  const exact = permanent ? "∞" : formatDateTime(record.time);

  return `
    <div class="countdown countdown--${level}" data-countdown
         data-expire="${record.time}" data-remaining="${remaining}"
         title="${escapeHtml(exact)}">
      <div class="countdown__text">
        <span data-countdown-text>${escapeHtml(text)}</span>
      </div>
      <div class="countdown__track">
        <span class="countdown__fill" data-countdown-fill style="width:${(ratio * 100).toFixed(1)}%"></span>
      </div>
    </div>`;
}

function reasonCell(record) {
  if (!record.reason) {
    return `<span class="reason reason--none">${escapeHtml(t("noReason"))}</span>`;
  }
  return `<span class="reason" title="${escapeHtml(record.reason)}">${escapeHtml(record.reason)}</span>`;
}

function rowActions(record) {
  const reset =
    record.scope === "global"
      ? `<button class="btn btn--ghost btn--sm" data-act="reset-user" data-id="${escapeHtml(record.id)}">${ICON.broom}<span>${escapeHtml(t("actionResetUser"))}</span></button>`
      : `<button class="btn btn--ghost btn--sm" data-act="reset-session" data-umo="${escapeHtml(record.umo)}">${ICON.broom}<span>${escapeHtml(t("actionResetSession"))}</span></button>`;

  return `
    <div class="row-actions">
      ${
        record.kind === "ban"
          ? `<button class="btn btn--pass btn--sm" data-act="pass" data-key="${recordKey(record)}">${ICON.pass}<span>${escapeHtml(t("actionPass"))}</span></button>`
          : `<button class="btn btn--danger btn--sm" data-act="ban" data-key="${recordKey(record)}">${ICON.ban}<span>${escapeHtml(t("actionBan"))}</span></button>`
      }
      <button class="btn btn--ghost btn--sm" data-act="extend" data-key="${recordKey(record)}">${ICON.plus}<span>${escapeHtml(t("actionExtend"))}</span></button>
      <button class="btn btn--ghost btn--sm" data-act="reduce" data-key="${recordKey(record)}">${ICON.minus}<span>${escapeHtml(t("actionReduce"))}</span></button>
      <button class="btn btn--ghost btn--sm" data-act="detail" data-key="${recordKey(record)}">${escapeHtml(t("detail"))}</button>
      ${reset}
      <button class="btn btn--ghost btn--sm" data-act="delete" data-key="${recordKey(record)}">${ICON.trash}<span>${escapeHtml(t("actionDelete"))}</span></button>
    </div>`;
}

/** Stable key so delegated clicks can find the record again. */
const recordKey = (record) =>
  `${record.kind}|${record.scope}|${record.id}|${record.umo || ""}|${record.target || "user"}`;

function findRecord(key) {
  return (
    state.records.find((item) => recordKey(item) === key) ||
    state.sessionRecords.find((item) => recordKey(item) === key) ||
    null
  );
}

function renderTable(rows) {
  const sortable = (key, label) => {
    const active = state.sort.key === key;
    const mark = active
      ? `<span class="sort-mark">${state.sort.dir === "asc" ? "▲" : "▼"}</span>`
      : "";
    return `<th class="is-sortable" data-sort="${key}">${escapeHtml(label)}${mark}</th>`;
  };

  return `
    <div class="panel__body panel__body--flush">
      <div class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              ${sortable("id", t("colTarget"))}
              ${sortable("scope", t("colScope"))}
              ${sortable("kind", t("colKind"))}
              ${sortable("remaining", t("colRemaining"))}
              ${sortable("reason", t("colReason"))}
              <th class="cell-actions">${escapeHtml(t("colActions"))}</th>
            </tr>
          </thead>
          <tbody>
            ${rows
              .map(
                (record) => `
              <tr data-key="${recordKey(record)}">
                <td>${identityCell(record)}</td>
                <td>${scopeBadge(record)}</td>
                <td>${kindBadge(record)}</td>
                <td>${countdownCell(record)}</td>
                <td>${reasonCell(record)}</td>
                <td class="cell-actions">${rowActions(record)}</td>
              </tr>`,
              )
              .join("")}
          </tbody>
        </table>
      </div>
    </div>`;
}

function renderCards(rows) {
  return `
    <div class="panel__body">
      <div class="cards">
        ${rows
          .map(
            (record) => `
          <article class="card" data-key="${recordKey(record)}">
            <div class="card__top">
              ${identityCell(record)}
              <div class="card__badges">${kindBadge(record)}</div>
            </div>
            <div class="card__meta">
              <div class="card__meta-row"><span class="card__meta-key">${escapeHtml(t("colScope"))}</span><span class="card__meta-val">${scopeBadge(record)}</span></div>
              <div class="card__meta-row"><span class="card__meta-key">${escapeHtml(t("colRemaining"))}</span><span class="card__meta-val">${countdownCell(record)}</span></div>
              <div class="card__meta-row"><span class="card__meta-key">${escapeHtml(t("colReason"))}</span><span class="card__meta-val">${reasonCell(record)}</span></div>
            </div>
            <div class="card__foot">
              ${
                record.kind === "ban"
                  ? `<button class="btn btn--pass btn--sm" data-act="pass" data-key="${recordKey(record)}">${ICON.pass}<span>${escapeHtml(t("actionPass"))}</span></button>`
                  : `<button class="btn btn--danger btn--sm" data-act="ban" data-key="${recordKey(record)}">${ICON.ban}<span>${escapeHtml(t("actionBan"))}</span></button>`
              }
              <button class="btn btn--ghost btn--sm" data-act="extend" data-key="${recordKey(record)}">${ICON.plus}</button>
              <button class="btn btn--ghost btn--sm" data-act="reduce" data-key="${recordKey(record)}">${ICON.minus}</button>
              <button class="btn btn--ghost btn--sm" data-act="detail" data-key="${recordKey(record)}">${escapeHtml(t("detail"))}</button>
              <button class="btn btn--ghost btn--sm" data-act="delete" data-key="${recordKey(record)}">${ICON.trash}</button>
            </div>
          </article>`,
          )
          .join("")}
      </div>
    </div>`;
}

function emptyState(searching) {
  return `
    <div class="empty">
      <div class="empty__icon">${searching ? ICON.search : ICON.empty}</div>
      <p class="empty__title">${escapeHtml(searching ? t("emptySearch") : t("empty"))}</p>
      <p class="empty__hint">${escapeHtml(searching ? t("search") : t("emptyHint"))}</p>
    </div>`;
}

function renderRecordPanel(rows) {
  const filtered = Boolean(state.search.trim()) ||
    state.filters.state !== "all" ||
    state.filters.kind !== "all" ||
    (state.filters.scope !== "all" && state.tab === "overview");

  const head = `
    <div class="panel__head">
      <h2 class="panel__title">${ICON.users}<span>${escapeHtml(
        state.tab === "global"
          ? t("tabGlobal")
          : state.tab === "session"
            ? t("tabSession")
            : state.tab === "sessionLevel"
              ? t("tabSessionLevel")
              : t("colTarget"),
      )}</span></h2>
      <span class="panel__hint">${rows.length} ${escapeHtml(t("unitRecords"))}</span>
    </div>`;

  if (rows.length === 0) {
    return `<section class="panel">${head}${emptyState(filtered)}</section>`;
  }
  return `<section class="panel">${head}${
    state.layout === "table" ? renderTable(rows) : renderCards(rows)
  }</section>`;
}

/* --- charts --- */

const BUCKET_LABEL = {
  lt1h: "bucketLt1h",
  lt6h: "bucketLt6h",
  lt24h: "bucketLt24h",
  lt3d: "bucketLt3d",
  lt7d: "bucketLt7d",
  gt7d: "bucketGt7d",
};

/**
 * Bento area: only meaningful while on the overview tab, and only when there is
 * something to plot.
 */
function renderBento() {
  const node = $("bento");
  const visible = state.tab === "overview" && state.records.length > 0;
  node.hidden = !visible;
  if (!visible) return;
  renderHeat();
  renderHistogram();
  renderMix();
  renderInsights();
  renderTimeline();
}

/** Seven-day expiry heat strip: 8 columns of 3 h per day. */
function renderHeat() {
  $("heatTitle").textContent = t("heatTitle");
  $("heatHint").textContent = t("heatHint");

  const cells = expiryHeat(7, 3);
  const peak = Math.max(1, ...cells.map((cell) => cell.bans + cell.passes));

  $("heat").innerHTML = cells
    .map((cell) => {
      const count = cell.bans + cell.passes;
      if (count === 0) {
        return `<span class="heat__cell" aria-hidden="true"></span>`;
      }
      const level = Math.round((0.3 + (count / peak) * 0.7) * 100);
      // Warm tint only for slots whose soonest record is under an hour away.
      const soonest = cell.offset;
      const kind =
        soonest <= 3600 ? "critical" : cell.passes > cell.bans ? "pass" : "ban";
      const record = cell.key ? findRecord(cell.key) : null;
      const when = record ? formatDateTime(record.time) : "";
      const title = `${when} · ${cell.bans} ${t("kindBan")} / ${cell.passes} ${t("kindPass")}`;
      return `<span class="heat__cell heat__cell--${kind}" style="--heat:${level}%;--heat-ratio:${(count / peak).toFixed(2)}" title="${escapeHtml(title)}" data-key="${escapeHtml(cell.key || "")}"></span>`;
    })
    .join("");

  // One axis label per day column, today first.
  const midnight = new Date();
  midnight.setHours(0, 0, 0, 0);
  $("heatAxis").innerHTML = Array.from({ length: 7 }, (_, index) => {
    const date = new Date(midnight.getTime() + index * 86400000);
    const label =
      index === 0
        ? t("heatToday")
        : date.toLocaleDateString(undefined, { month: "2-digit", day: "2-digit" });
    return `<span>${escapeHtml(label)}</span>`;
  }).join("");

  $("heatLegend").innerHTML = `
    <span class="heat-scale">${escapeHtml(t("heatLess"))}
      <i style="--heat:30%"></i><i style="--heat:55%"></i><i style="--heat:80%"></i><i style="--heat:100%"></i>
      ${escapeHtml(t("heatMore"))}</span>
    <span>${escapeHtml(t("heatAxisHint"))}</span>`;
}

function renderHistogram() {
  const buckets = state.buckets;
  $("histTitle").textContent = t("histTitle");
  $("histHint").textContent = t("histHint");

  const max = Math.max(1, ...buckets.map((bucket) => bucket.count));
  $("histogram").innerHTML = buckets
    .map((bucket) => {
      const label = t(BUCKET_LABEL[bucket.key] || bucket.key);
      if (bucket.count === 0) {
        return `
          <div class="hist" title="${escapeHtml(`${label}: 0`)}">
            <span class="hist__count is-zero">0</span>
            <span class="hist__ghost"></span>
            <span class="hist__label">${escapeHtml(label)}</span>
          </div>`;
      }
      // Stacked bar: bans at the bottom, exemptions on top. The tallest column
      // owns the full plot height, the rest scale against it.
      const height = 16 + (bucket.count / max) * 74;
      const banShare = bucket.bans / bucket.count;
      const segments = [
        `<span class="hist__seg hist__seg--ban" style="height:${(banShare * 100).toFixed(1)}%"></span>`,
        bucket.passes > 0
          ? `<span class="hist__seg hist__seg--pass" style="height:${((1 - banShare) * 100).toFixed(1)}%"></span>`
          : "",
      ].join("");
      return `
        <div class="hist" title="${escapeHtml(`${label}: ${bucket.count}`)}">
          <span class="hist__count">${bucket.count}</span>
          <span class="hist__stack" style="height:${height.toFixed(1)}%">${segments}</span>
          <span class="hist__label">${escapeHtml(label)}</span>
        </div>`;
    })
    .join("");

  $("histLegend").innerHTML = `
    <span class="chart-legend__item"><span class="chart-legend__swatch chart-legend__swatch--ban"></span>${escapeHtml(t("kindBan"))}</span>
    <span class="chart-legend__item"><span class="chart-legend__swatch chart-legend__swatch--pass"></span>${escapeHtml(t("kindPass"))}</span>
    <span class="chart-legend__item"><span class="chart-legend__swatch chart-legend__swatch--idle"></span>${escapeHtml(t("statPermanent"))}: <strong class="num">${state.stats.permanent ?? 0}</strong></span>`;
}

function renderMix() {
  $("mixTitle").textContent = t("mixTitle");
  // stats.* covers user-scoped records only; the session-level records are
  // charted in the histogram, so the caption says so.
  $("mixHint").textContent = t("mixHint");

  const total = Number(state.stats.total) || 0;
  const bans = Number(state.stats.bans) || 0;
  const passes = Number(state.stats.passes) || 0;
  const permanent = Number(state.stats.permanent) || 0;
  const temporary = Number(state.stats.temporary) || 0;

  if (total === 0) {
    $("mixBody").innerHTML = `
      <div class="empty" style="padding:26px 8px">
        <div class="empty__icon">${ICON.pie}</div>
        <p class="empty__title">${escapeHtml(t("empty"))}</p>
      </div>`;
    return;
  }

  // The two arcs always fill the ring between them, so they read as a whole.
  const banAngle = (bans / total) * 360;
  const gap = total > 1 ? 3 : 0;
  const banSpan = Math.max(banAngle - gap, 0);
  const passSpan = Math.max(360 - banAngle - gap, 0);

  const row = (modifier, name, value) => {
    const share = Math.round((value / total) * 100);
    return `
      <div class="donut__row">
        <span class="donut__dot donut__dot--${modifier}"></span>
        <span class="donut__name">${escapeHtml(name)}</span>
        <span class="donut__value num">${value}<span class="donut__share">${share}%</span></span>
      </div>`;
  };

  $("mixBody").innerHTML = `
    <div class="donut">
      <figure class="donut__figure">
        <svg viewBox="0 0 120 120" role="img" aria-label="${escapeHtml(`${t("mixTitle")}: ${bans} / ${passes}`)}">
          <circle class="donut__track" cx="60" cy="60" r="46"></circle>
          <circle class="donut__arc donut__arc--ban" cx="60" cy="60" r="46"
                  stroke-dasharray="${(banSpan / 360) * 289.03} 289.03"
                  style="--dash:${((banSpan / 360) * 289.03).toFixed(1)}"></circle>
          <circle class="donut__arc donut__arc--pass" cx="60" cy="60" r="46"
                  stroke-dasharray="0 ${((banAngle / 360) * 289.03).toFixed(2)} ${((passSpan / 360) * 289.03).toFixed(2)} 289.03"
                  style="--dash:${((passSpan / 360) * 289.03).toFixed(1)}"></circle>
        </svg>
        <div class="donut__center">
          <span class="donut__total num">${total}</span>
          <span class="donut__caption">${escapeHtml(t("unitRecords"))}</span>
        </div>
      </figure>
      <div class="donut__legend">
        ${row("ban", t("mixBans"), bans)}
        ${row("pass", t("mixPasses"), passes)}
        ${row("idle", t("mixPermanent"), permanent)}
        ${row("idle", t("mixTemporary"), temporary)}
      </div>
    </div>`;
}

function renderInsights() {
  $("insightTitle").textContent = t("insightTitle");
  $("heatTitle").textContent = t("heatTitle");
  $("heatHint").textContent = t("heatHint");
  const { nextExpiry, topUser, topSession } = state.insights || {};
  const rows = [];

  if (nextExpiry) {
    rows.push(`
      <button class="insight" type="button" data-act="detail" data-key="${recordKey(nextExpiry)}">
        <span class="insight__icon insight__icon--warn">${ICON.hourglass}</span>
        <span class="insight__body">
          <span class="insight__title">${escapeHtml(t("insightNextExpiry"))}</span>
          <span class="insight__value mono">${escapeHtml(nextExpiry.id)}</span>
          <span class="insight__meta">${escapeHtml(nextExpiry.session_name || t("scopeGlobal"))} · ${escapeHtml(formatDateTime(nextExpiry.time))}</span>
        </span>
        <span class="insight__side">${escapeHtml(formatDuration(nextExpiry.remaining))}</span>
      </button>`);
  }

  if (topUser) {
    rows.push(`
      <div class="insight">
        <span class="insight__icon">${ICON.crown}</span>
        <span class="insight__body">
          <span class="insight__title">${escapeHtml(t("insightTopUser"))}</span>
          <span class="insight__value mono">${escapeHtml(topUser.id)}</span>
          <span class="insight__meta">${topUser.bans} ${escapeHtml(t("kindBan"))} · ${topUser.passes} ${escapeHtml(t("kindPass"))}</span>
        </span>
        <span class="insight__side">${topUser.count}</span>
      </div>`);
  }

  if (topSession) {
    rows.push(`
      <button class="insight" type="button" data-act="pick-session" data-umo="${escapeHtml(topSession.umo)}">
        <span class="insight__icon insight__icon--brand">${ICON.layers}</span>
        <span class="insight__body">
          <span class="insight__title">${escapeHtml(t("insightTopSession"))}</span>
          <span class="insight__value">${escapeHtml(topSession.session_name || topSession.umo)}</span>
          <span class="insight__meta mono">${escapeHtml(topSession.umo)}</span>
        </span>
        <span class="insight__side">${topSession.total}</span>
      </button>`);
  }

  $("insights").innerHTML = rows.length
    ? rows.join("")
    : `<div class="empty" style="padding:26px 16px">
         <div class="empty__icon">${ICON.spark}</div>
         <p class="empty__title">${escapeHtml(t("empty"))}</p>
         <p class="empty__hint">${escapeHtml(t("emptyHint"))}</p>
       </div>`;
}

function renderTimeline() {
  $("timelineTitle").textContent = t("timelineTitle");
  $("timelineHint").textContent = t("timelineHint");
  const node = $("timeline");

  const rows = state.records
    .filter((item) => item.time !== 0 && item.remaining > 0)
    .sort((a, b) => a.time - b.time)
    .slice(0, 8);

  if (rows.length === 0) {
    node.innerHTML = `<div class="empty" style="padding:26px 16px">
        <div class="empty__icon">${ICON.ok}</div>
        <p class="empty__title">${escapeHtml(t("timelineEmpty"))}</p>
      </div>`;
    return;
  }

  node.innerHTML = `<div class="timeline">${rows
    .map((record) => {
      const ratio = clamp(record.remaining / BAR_REFERENCE, 0.02, 1);
      const far = record.remaining > 86400;
      const where = record.scope === "global" ? t("scopeGlobal") : record.session_name;
      return `
        <div class="timeline__row${record.remaining <= 3600 ? " is-critical" : ""}" data-key="${recordKey(record)}">
          <span class="timeline__when${far ? " is-far" : ""}" title="${escapeHtml(formatDateTime(record.time))}">${escapeHtml(formatDuration(record.remaining))}${
            far ? `<span class="timeline__date">${escapeHtml(formatDate(record.time))}</span>` : ""
          }</span>
          <span class="timeline__who" title="${escapeHtml(record.id)}">${escapeHtml(record.id)}<span class="mono">${escapeHtml(where || "")}</span></span>
          <span class="badge badge--${record.kind}">${escapeHtml(record.kind === "ban" ? t("kindBan") : t("kindPass"))}</span>
          <span class="timeline__track"><span class="timeline__fill" style="width:${(ratio * 100).toFixed(1)}%"></span></span>
        </div>`;
    })
    .join("")}</div>`;
}

function renderSessions() {
  if (state.sessions.length === 0) {
    return `<section class="panel"><div class="panel__head"><h2 class="panel__title">${ICON.chat}<span>${escapeHtml(t("sessionsTitle"))}</span></h2></div>${emptyState(false)}</section>`;
  }
  const cards = state.sessions
    .map(
      (session) => `
      <button class="session-card" data-act="pick-session" data-umo="${escapeHtml(session.umo)}" type="button">
        <span class="session-card__name" title="${escapeHtml(session.session_name)}">${escapeHtml(session.session_name)}</span>
        <span class="session-card__umo" title="${escapeHtml(session.umo)}">${escapeHtml(session.umo)}</span>
        <span class="session-card__counts">
          <span class="badge badge--ban" title="${escapeHtml(t("sessionBans"))}">${ICON.ban}${session.bans}</span>
          <span class="badge badge--pass" title="${escapeHtml(t("sessionPasses"))}">${ICON.pass}${session.passes}</span>
          <span class="badge badge--muted">${escapeHtml(prettyMessageType(session.message_type))}</span>
        </span>
      </button>`,
    )
    .join("");

  return `
    <section class="panel">
      <div class="panel__head">
        <h2 class="panel__title">${ICON.chat}<span>${escapeHtml(t("sessionsTitle"))}</span></h2>
        <div class="row-actions" style="opacity:1">
          <button class="btn btn--ghost btn--sm" data-act="create-session-ban">${ICON.ban}<span>${escapeHtml(t("actionBan"))}</span></button>
          <button class="btn btn--pass btn--sm" data-act="create-session-pass">${ICON.pass}<span>${escapeHtml(t("actionPass"))}</span></button>
        </div>
      </div>
      <div class="panel__body"><div class="session-grid">${cards}</div></div>
    </section>`;
}

function renderContent() {
  const node = $("content");
  if (state.error && state.records.length === 0 && state.sessionRecords.length === 0) {
    node.innerHTML = `<section class="panel">${emptyState(false)}</section>`;
    return;
  }

  if (state.tab === "overview") {
    node.innerHTML = renderRecordPanel(currentRecords());
    return;
  }
  if (state.tab === "sessions") {
    node.innerHTML = renderSessions();
    return;
  }
  node.innerHTML = renderRecordPanel(currentRecords());
}

/* ------------------------------------------------------------------ *
 * countdown ticker
 * ------------------------------------------------------------------ */

function tickCountdowns() {
  const now = Math.floor(Date.now() / 1000);
  document.querySelectorAll("[data-countdown]").forEach((node) => {
    const expire = Number(node.dataset.expire || 0);
    if (expire === 0) return;
    const remaining = expire - now;
    node.dataset.remaining = String(Math.max(0, remaining));
    const text = node.querySelector("[data-countdown-text]");
    const fill = node.querySelector("[data-countdown-fill]");
    const level =
      remaining <= 0
        ? "critical"
        : remaining <= 3600
          ? "critical"
          : remaining <= 86400
            ? "warn"
            : "calm";
    node.classList.remove("countdown--critical", "countdown--warn", "countdown--calm");
    node.classList.add(`countdown--${level}`);

    if (remaining <= 0) {
      if (text) text.textContent = t("expired");
      if (fill) fill.style.width = "100%";
      return;
    }
    if (text) text.textContent = formatDuration(remaining);
    if (fill) {
      fill.style.width = `${(clamp(remaining / BAR_REFERENCE, 0.015, 1) * 100).toFixed(1)}%`;
    }
  });
}

/* ------------------------------------------------------------------ *
 * toasts
 * ------------------------------------------------------------------ */

function toast(kind, title, message) {
  const node = document.createElement("div");
  node.className = `toast toast--${kind === "ok" ? "ok" : "err"}`;
  node.innerHTML = `
    ${kind === "ok" ? ICON.ok : ICON.alert}
    <div class="toast__body">
      <div class="toast__title">${escapeHtml(title || "")}</div>
      ${message ? `<div class="toast__msg">${escapeHtml(message)}</div>` : ""}
    </div>`;
  $("toasts").appendChild(node);
  setTimeout(() => {
    node.classList.add("is-leaving");
    setTimeout(() => node.remove(), 220);
  }, 3400);
}

/* ------------------------------------------------------------------ *
 * modal
 * ------------------------------------------------------------------ */

function closeModal() {
  state.modal = null;
  const modal = $("modal");
  modal.hidden = true;
  $("modalBody").innerHTML = "";
  $("modalFoot").innerHTML = "";
  // Release the background. Hiding the overlay can reset the scroll offset, so
  // the remembered position is restored rather than assumed to survive.
  document.documentElement.classList.remove("is-dialog-open");
  if (state.pageScrollY) {
    window.scrollTo(0, state.pageScrollY);
    state.pageScrollY = 0;
  }
}

function openModal({ title, body, foot, onMount }) {
  state.modal = { title };
  $("modalTitle").textContent = title;
  $("modalBody").innerHTML = body;
  $("modalFoot").innerHTML = foot;
  // The dialog is fixed to the viewport, so a swipe outside its own scroll area
  // would otherwise scroll the page behind it out of sight.
  state.pageScrollY = window.scrollY || 0;
  document.documentElement.classList.add("is-dialog-open");
  $("modal").hidden = false;
  onMount?.();
  const focusTarget = $("modalBody").querySelector("input, select, textarea, button");
  focusTarget?.focus();
}

function fieldId(label, control, hint) {
  return `
    <label class="field">
      <span class="field__label">${escapeHtml(label)}</span>
      ${control}
      ${hint ? `<span class="field__hint">${escapeHtml(hint)}</span>` : ""}
    </label>`;
}

const durationChips = (prefix) => `
  <div class="field">
    <span class="field__label">${escapeHtml(t("durationPreset"))}</span>
    <div class="chips" data-chips="${prefix}">
      ${[
        ["1h", t("preset1h")],
        ["1d", t("preset1d")],
        ["7d", t("preset7d")],
        ["30d", t("preset30d")],
        ["0", t("presetForever")],
      ]
        .map(
          ([value, label]) =>
            `<button class="chip" type="button" data-chip-value="${value}">${escapeHtml(label)}</button>`,
        )
        .join("")}
    </div>
  </div>`;

/**
 * Session picker. Falls back to a free text input when the sessions list is
 * empty, so the dialog still works on an instance without recordings.
 * When `locked` is set the value is fixed to `preset` (editing one record).
 */
function sessionField(preset, locked) {
  if (locked && preset) {
    return `
      <input class="input mono" id="fUmo" value="${escapeHtml(preset)}" readonly />
      <span class="field__hint">${escapeHtml(preset)}</span>`;
  }
  if (state.sessions.length === 0) {
    return `<input class="input mono" id="fUmo" placeholder="platform:GroupMessage:123456" autocomplete="off" />`;
  }
  return `
    <select class="select" id="fUmo">
      <option value="">${escapeHtml(t("selectSession"))}</option>
      ${state.sessions
        .map(
          (session) =>
            `<option value="${escapeHtml(session.umo)}"${session.umo === preset ? " selected" : ""}>${escapeHtml(session.session_name)} — ${escapeHtml(session.umo)}</option>`,
        )
        .join("")}
    </select>`;
}

function scopeSegmented(active, disabled) {
  return `
    <div class="segmented" data-segmented="scope" data-disabled="${disabled ? "1" : "0"}">
      <button class="segmented__btn${active === "session" ? " is-active" : ""}" data-value="session" type="button"${disabled ? " disabled" : ""}>${escapeHtml(t("scopeSession"))}</button>
      <button class="segmented__btn${active === "global" ? " is-active" : ""}" data-value="global" type="button"${disabled ? " disabled" : ""}>${escapeHtml(t("scopeGlobal"))}</button>
    </div>`;
}

function targetSegmented(active, allowUser = true) {
  return `
    <div class="segmented" data-segmented="target">
      <button class="segmented__btn${active === "user" ? " is-active" : ""}" data-value="user" type="button"${allowUser ? "" : " disabled"}>${escapeHtml(t("fieldTargetUser"))}</button>
      <button class="segmented__btn${active === "session" ? " is-active" : ""}" data-value="session" type="button">${escapeHtml(t("fieldTargetSession"))}</button>
    </div>`;
}

/** Build the ban / pass dialog. */
function openActionDialog({ kind, preset = {} }) {
  const isBan = kind === "ban";
  const title = isBan ? t("dialogBanTitle") : t("dialogPassTitle");
  // Existing records are edited in place, so the session is fixed.
  const locked = Boolean(preset.umo && preset.id);
  const initial = {
    scope: preset.scope || (preset.umo ? "session" : "global"),
    target: preset.target || "user",
    id: preset.id || "",
    umo: preset.umo || "",
  };

  const body = `
    <div class="form-grid">
      ${fieldId(t("fieldTarget"), targetSegmented(initial.target))}
      ${fieldId(t("fieldScope"), scopeSegmented(initial.scope))}
    </div>
    <div class="form-grid">
      <div class="field" data-when="user">
        <span class="field__label">${escapeHtml(t("fieldId"))}</span>
        <input class="input mono" id="fId" value="${escapeHtml(initial.id)}" placeholder="123456789" autocomplete="off" />
      </div>
      <div class="field" data-when="session">
        <span class="field__label">${escapeHtml(t("fieldUmo"))}</span>
        ${sessionField(initial.umo, locked)}
      </div>
    </div>
    <div class="form-grid">
      <div class="field">
        <span class="field__label">${escapeHtml(t("fieldDuration"))}</span>
        <input class="input" id="fDuration" value="1d" autocomplete="off" />
        <span class="field__hint">${escapeHtml(t("durationHint"))}</span>
      </div>
    </div>
    ${durationChips("duration")}
    ${fieldId(t("fieldReason"), `<input class="input" id="fReason" autocomplete="off" />`, t("reasonHint"))}
  `;

  const foot = `
    <button class="btn btn--ghost" data-modal="cancel" type="button">${escapeHtml(t("cancel"))}</button>
    <button class="btn ${isBan ? "btn--danger" : "btn--pass"}" data-modal="submit" type="button">
      ${isBan ? ICON.ban : ICON.pass}<span>${escapeHtml(title)}</span>
    </button>`;

  openModal({
    title,
    body,
    foot,
    onMount: () => {
      const sync = () => {
        const target = $("modalBody").querySelector("[data-segmented='target'] .is-active")
          ?.dataset.value;
        $("modalBody")
          .querySelectorAll("[data-when]")
          .forEach((node) => {
            node.hidden = node.dataset.when !== target;
          });
      };
      if (locked) {
        // Both segmented controls are fixed when editing one record.
        $("modalBody")
          .querySelectorAll(".segmented__btn")
          .forEach((button) => {
            button.disabled = true;
          });
      }
      sync();
      $("modalBody")
        .querySelectorAll(".chip")
        .forEach((chip) =>
          chip.addEventListener("click", () => {
            $("fDuration").value = chip.dataset.chipValue;
            $("modalBody")
              .querySelectorAll(".chip")
              .forEach((other) => other.classList.toggle("is-active", other === chip));
          }),
        );
      $("modalBody").addEventListener("click", (event) => {
        const button = event.target.closest(".segmented__btn");
        if (!button || button.disabled) return;
        const group = button.closest("[data-segmented]");
        group
          .querySelectorAll(".segmented__btn")
          .forEach((other) => other.classList.toggle("is-active", other === button));
        sync();
      });
    },
  });

  state.modal = {
    title,
    submit: async () => {
      const target =
        $("modalBody").querySelector("[data-segmented='target'] .is-active")?.dataset
          .value || "user";
      const scope =
        $("modalBody").querySelector("[data-segmented='scope'] .is-active")?.dataset
          .value || "global";
      const id = $("fId")?.value.trim() || initial.id;
      const umo = $("fUmo")?.value.trim() || initial.umo;
      const durationText = $("fDuration")?.value.trim() ?? "";
      const reason = $("fReason")?.value.trim() || "";

      if (target === "user" && !id) {
        toast("err", t("fieldRequired"), t("fieldId"));
        return;
      }
      if (scope === "session" && !umo) {
        toast("err", t("fieldRequired"), t("fieldUmo"));
        return;
      }
      const seconds = parseDurationToSeconds(durationText || "0");
      if (seconds === null) {
        toast("err", t("opFailed"), t("durationHint"));
        return;
      }

      const payload = { scope, target, duration: seconds, reason };
      // Session level records address their session through `id`.
      payload.id = target === "session" ? umo : id;
      if (scope === "session") payload.umo = umo;

      const ok = await mutate(isBan ? "ban" : "pass", payload, title);
      if (ok) closeModal();
    },
  };
}

/** Build the extend / shorten dialog. */
function openShiftDialog({ record, direction }) {
  const extend = direction === "extend";
  const title = extend ? t("dialogExtendTitle") : t("dialogReduceTitle");
  const body = `
    <div class="detail-list">
      <div class="detail-row"><span class="detail-row__key">${escapeHtml(t("colTarget"))}</span><span class="detail-row__val mono">${escapeHtml(record.id)}</span></div>
      <div class="detail-row"><span class="detail-row__key">${escapeHtml(t("colScope"))}</span><span class="detail-row__val">${escapeHtml(record.scope === "global" ? t("scopeGlobal") : record.session_name || record.umo)}</span></div>
      <div class="detail-row"><span class="detail-row__key">${escapeHtml(t("colRemaining"))}</span><span class="detail-row__val">${escapeHtml(record.time === 0 ? t("permanent") : formatDuration(record.remaining))}</span></div>
    </div>
    ${fieldId(
      t("fieldDelta"),
      `<input class="input" id="fDelta" value="${extend ? "1d" : "1h"}" autocomplete="off" />`,
      t("deltaHint"),
    )}
    ${durationChips("delta")}
    ${fieldId(t("fieldReason"), `<input class="input" id="fReason" autocomplete="off" />`, t("reasonHint"))}
  `;
  const foot = `
    <button class="btn btn--ghost" data-modal="cancel" type="button">${escapeHtml(t("cancel"))}</button>
    <button class="btn ${extend ? "btn--primary" : "btn--danger"}" data-modal="submit" type="button">
      ${extend ? ICON.plus : ICON.minus}<span>${escapeHtml(title)}</span>
    </button>`;

  openModal({
    title,
    body,
    foot,
    onMount: () => {
      $("modalBody").querySelectorAll(".chip").forEach((chip) =>
        chip.addEventListener("click", () => {
          $("fDelta").value = chip.dataset.chipValue;
          $("modalBody")
            .querySelectorAll(".chip")
            .forEach((other) => other.classList.toggle("is-active", other === chip));
        }),
      );
    },
  });

  state.modal = {
    title,
    submit: async () => {
      const text = $("fDelta")?.value.trim() ?? "";
      const seconds = parseDurationToSeconds(text);
      if (seconds === null || seconds === 0) {
        toast("err", t("opFailed"), t("deltaHint"));
        return;
      }
      const payload = {
        scope: record.scope,
        kind: record.kind,
        target: record.target || "user",
        id: record.id,
        delta: extend ? seconds : -seconds,
        reason: $("fReason")?.value.trim() || "",
      };
      if (record.scope === "session") payload.umo = record.umo;
      const ok = await mutate("shift", payload, title);
      if (ok) closeModal();
    },
  };
}

/**
 * Build a confirm dialog.
 *
 * `tone` picks how alarming the note and the confirm button look:
 * `critical` for irreversible deletions, `brand` for state changes that are
 * meaningful but reversible.
 */
function openConfirmDialog({
  title,
  message,
  confirmLabel,
  danger = true,
  tone,
  note,
  onConfirm,
}) {
  const resolvedTone = tone || (danger ? "critical" : "brand");
  const body = `
    <div class="${resolvedTone === "critical" ? "danger-note" : "info-note"}">${
      resolvedTone === "critical" ? ICON.warn : ICON.info
    }<span>${escapeHtml(message)}</span></div>
    ${note ? `<p class="confirm-note">${escapeHtml(note)}</p>` : ""}`;
  const toneClass =
    resolvedTone === "critical" ? "btn--danger" : resolvedTone === "pass" ? "btn--pass" : "btn--primary";
  const foot = `
    <button class="btn btn--ghost" data-modal="cancel" type="button">${escapeHtml(t("cancel"))}</button>
    <button class="btn ${toneClass}" data-modal="submit" type="button">${escapeHtml(confirmLabel || t("confirm"))}</button>`;

  openModal({ title, body, foot });
  state.modal = {
    title,
    submit: async () => {
      const ok = await onConfirm();
      if (ok) closeModal();
    },
  };
}

/** Build the read-only detail dialog. */
function openDetailDialog(record) {
  const rows = [
    [t("colTarget"), record.id],
    [t("colScope"), record.scope === "global" ? t("scopeGlobal") : t("scopeSession")],
    [t("colKind"), record.kind === "ban" ? t("kindBan") : t("kindPass")],
    [t("fieldUmo"), record.umo || "—"],
    [t("sessionIdLabel"), record.session_id || "—"],
    [t("platformLabel"), record.platform || "—"],
    [t("msgTypeLabel"), prettyMessageType(record.message_type)],
    [t("colRemaining"), record.time === 0 ? t("permanent") : formatDuration(record.remaining)],
    [t("colExpireAt"), record.time === 0 ? t("permanent") : formatDateTime(record.time)],
    [t("colReason"), record.reason || t("noReason")],
  ];

  const body = `
    <div class="detail-list">
      ${rows
        .map(
          ([key, value]) => `
        <div class="detail-row">
          <span class="detail-row__key">${escapeHtml(key)}</span>
          <span class="detail-row__val${key === t("fieldUmo") || key === t("colTarget") ? " mono" : ""}">${escapeHtml(value)}</span>
        </div>`,
        )
        .join("")}
    </div>`;

  const foot = `
    <button class="btn btn--ghost grow" data-modal="copy" type="button">${ICON.copy}<span>${escapeHtml(t("actionCopyUmo"))}</span></button>
    <button class="btn btn--primary" data-modal="cancel" type="button">${escapeHtml(t("close"))}</button>`;

  openModal({ title: t("detail"), body, foot });
  state.modal = {
    title: t("detail"),
    copyValue: record.umo || record.id,
    submit: () => closeModal(),
  };
}

async function copyText(value) {
  try {
    await navigator.clipboard.writeText(value);
  } catch {
    const area = document.createElement("textarea");
    area.value = value;
    area.style.position = "fixed";
    area.style.opacity = "0";
    document.body.appendChild(area);
    area.select();
    document.execCommand("copy");
    area.remove();
  }
  toast("ok", t("copied"), value);
}

/* ------------------------------------------------------------------ *
 * event wiring
 * ------------------------------------------------------------------ */

function handleAction(action, node) {
  const key = node.dataset.key;
  const record = key ? findRecord(key) : null;

  switch (action) {
    case "detail":
      if (record) openDetailDialog(record);
      return;
    case "copy":
      if (record) copyText(record.umo || record.id);
      return;
    case "extend":
      if (record) openShiftDialog({ record, direction: "extend" });
      return;
    case "reduce":
      if (record) openShiftDialog({ record, direction: "reduce" });
      return;
    case "delete":
      if (!record) return;
      openConfirmDialog({
        title: t("dialogDeleteTitle"),
        message: t("confirmDelete"),
        confirmLabel: t("actionDelete"),
        onConfirm: () =>
          mutate(
            "delete",
            {
              scope: record.scope,
              kind: record.kind,
              id: record.id,
              umo: record.umo,
              target: record.target || "user",
            },
            t("actionDelete"),
          ),
      });
      return;
    case "reset-user":
      openConfirmDialog({
        title: t("dialogResetUserTitle"),
        message: t("confirmResetUser"),
        confirmLabel: t("actionResetUser"),
        onConfirm: () =>
          mutate("reset-user", { id: node.dataset.id }, t("actionResetUser")),
      });
      return;
    case "reset-session":
      openConfirmDialog({
        title: t("dialogResetSessionTitle"),
        message: t("confirmResetSession"),
        confirmLabel: t("actionResetSession"),
        onConfirm: () =>
          mutate("reset-session", { umo: node.dataset.umo }, t("actionResetSession")),
      });
      return;
    case "pass":
      if (record) {
        openActionDialog({
          kind: "pass",
          preset: {
            id: record.id,
            umo: record.umo,
            scope: record.scope,
            target: record.target || "user",
          },
        });
      }
      return;
    case "ban":
      if (record) {
        openActionDialog({
          kind: "ban",
          preset: {
            id: record.id,
            umo: record.umo,
            scope: record.scope,
            target: record.target || "user",
          },
        });
      }
      return;
    case "create-session-ban":
      openActionDialog({ kind: "ban", preset: { target: "session", scope: "session" } });
      return;
    case "create-session-pass":
      openActionDialog({
        kind: "pass",
        preset: { target: "session", scope: "session" },
      });
      return;
    case "pick-session": {
      state.search = node.dataset.umo;
      $("searchInput").value = state.search;
      state.tab = "session";
      render();
      return;
    }
    default:
  }
}

function wireEvents() {
  $("app").addEventListener("click", (event) => {
    const tab = event.target.closest("[data-tab]");
    if (tab) {
      state.tab = tab.dataset.tab;
      render();
      return;
    }

    const sortHeader = event.target.closest("th[data-sort]");
    if (sortHeader) {
      const key = sortHeader.dataset.sort;
      state.sort =
        state.sort.key === key
          ? { key, dir: state.sort.dir === "asc" ? "desc" : "asc" }
          : { key, dir: "asc" };
      render();
      return;
    }

    const layoutBtn = event.target.closest("[data-layout]");
    if (layoutBtn) {
      state.layout = layoutBtn.dataset.layout;
      render();
      return;
    }

    const actionNode = event.target.closest("[data-act]");
    if (actionNode) {
      handleAction(actionNode.dataset.act, actionNode);
    }
  });

  $("searchInput").addEventListener("input", (event) => {
    state.search = event.target.value;
    renderContent();
  });

  // The filter dropdowns are rebuilt on every render, so their change handlers
  // are attached in renderFilterOptions() rather than here.

  $("refreshBtn").addEventListener("click", () => refresh());
  $("createBtn").addEventListener("click", () =>
    openActionDialog({
      kind: "ban",
      preset: {
        target: state.tab === "sessionLevel" ? "session" : "user",
        scope: state.tab === "global" ? "global" : "session",
      },
    }),
  );

  // The switch flips the live filter, which starts or stops blocking people
  // right away, so it asks for confirmation instead of applying on one click.
  $("enableSwitch").addEventListener("click", () => {
    const next = !state.enabled;
    openConfirmDialog({
      title: next ? t("confirmEnableTitle") : t("confirmDisableTitle"),
      message: next ? t("confirmEnableBody") : t("confirmDisableBody"),
      note: t("enableConfirmNote"),
      confirmLabel: next ? t("enableAction") : t("disableAction"),
      tone: next ? "critical" : "brand",
      // Shown for both directions: the switch is runtime-only either way.
      note: t("enableConfirmNote"),
      onConfirm: () =>
        mutate("toggle", { enabled: next }, next ? t("enableOn") : t("enableOff")),
    });
  });

  $("fatalRetry").addEventListener("click", () => {
    $("fatal").hidden = true;
    $("boot").hidden = false;
    refresh();
  });

  // Modal: delegation covers buttons created after mount. The header close
  // button is part of the static shell, so it is matched explicitly rather than
  // relying on an attribute a future edit could drop.
  $("modal").addEventListener("click", async (event) => {
    if (event.target.closest("[data-close]")) {
      closeModal();
      return;
    }
    if (event.target.closest("#modalClose")) {
      closeModal();
      return;
    }
    const button = event.target.closest("[data-modal]");
    if (!button) return;
    const action = button.dataset.modal;
    if (action === "cancel") {
      closeModal();
      return;
    }
    if (action === "copy") {
      const value = state.modal?.copyValue;
      if (value) copyText(value);
      return;
    }
    if (action === "submit") {
      button.disabled = true;
      try {
        await state.modal?.submit?.();
      } finally {
        button.disabled = false;
      }
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !$("modal").hidden) {
      closeModal();
      return;
    }
    if (event.target.matches("input, textarea, select")) return;
    if (event.key === "r" || event.key === "R") refresh();
    if (event.key === "/") {
      event.preventDefault();
      $("searchInput").focus();
    }
  });
}

/* ------------------------------------------------------------------ *
 * bootstrap
 * ------------------------------------------------------------------ */

async function boot() {
  const ready = bridge?.ready?.() ?? Promise.resolve(DEFAULT_CONTEXT);
  const context = await Promise.race([
    ready,
    new Promise((resolve) => setTimeout(() => resolve(DEFAULT_CONTEXT), 2500)),
  ]).catch(() => DEFAULT_CONTEXT);

  applyTheme(Boolean(context?.isDark));
  bridge?.onContext?.((next) => {
    applyTheme(Boolean(next?.isDark));
    render();
  });

  wireEvents();
  hydrateIcons();
  setInterval(tickCountdowns, 1000);

  // Lift the sticky bar onto its blurred surface once the page scrolls.
  const topbar = $("topbar");
  const onScroll = () => topbar.classList.toggle("is-stuck", window.scrollY > 4);
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  $("bootText").textContent = t("loading");
  try {
    await loadData();
    state.error = null;
    showApp();
    render();
  } catch (error) {
    showFatal(error?.message || String(error));
  }
}

boot();
