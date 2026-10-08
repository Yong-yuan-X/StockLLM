        const BASE_API_URL = `${window.location.origin}/api`;
        const STOCK_PAGE_SIZE = 20;
        const SECTOR_PAGE_SIZE = 10;
const USER_STORAGE_KEY = 'stockllm-current-user';
        let currentUser = null;

        const stockCodeInput = document.getElementById('stockCodeInput');
        const favoriteStockSelect = document.getElementById('favoriteStockSelect');
        const sendReportBtn = document.getElementById('sendReportBtn');
        const updateResult = document.getElementById('updateResult');
        const updateResultContent = document.getElementById('updateResultContent');
        const predictRunBtn = document.getElementById('predictRunBtn');
        const predictResult = document.getElementById('predictResult');
        const predictResultContent = document.getElementById('predictResultContent');
        const reportResult = document.getElementById('reportResult');
        const reportResultContent = document.getElementById('reportResultContent');
        const historyReportResult = document.getElementById('historyReportResult');
        const historyReportContent = document.getElementById('historyReportContent');
        const historyReportStandaloneContent = document.getElementById('historyReportStandaloneContent');
        const analysisProgress = document.getElementById('analysisProgress');
        const analysisProgressText = document.getElementById('analysisProgressText');
        const authOverlay = document.getElementById('authOverlay');
        const authSubmitBtn = document.getElementById('authSubmitBtn');
        const authSwitchBtn = document.getElementById('authSwitchBtn');
        const authForgotBtn = document.getElementById('authForgotBtn');
        const authUsernameInput = document.getElementById('authUsernameInput');
        const authEmailInput = document.getElementById('authEmailInput');
        const authEmailCodeInput = document.getElementById('authEmailCodeInput');
        const authCodeRow = document.getElementById('authCodeRow');
        const sendEmailCodeBtn = document.getElementById('sendEmailCodeBtn');
        const authPasswordInput = document.getElementById('authPasswordInput');
        const authStatus = document.getElementById('authStatus');
        const authStatusText = document.getElementById('authStatusText');
        const sidebarUserAvatar = document.getElementById('sidebarUserAvatar');
        const sidebarUsername = document.getElementById('sidebarUsername');
        const sidebarUserMeta = document.getElementById('sidebarUserMeta');
        const logoutBtn = document.getElementById('logoutBtn');
        const userManageMenuItem = document.getElementById('userManageMenuItem');
        const adminUsersCard = document.getElementById('adminUsersCard');
        const adminUsersBody = document.getElementById('adminUsersBody');
        const marketAnalysisIndexSelect = document.getElementById('marketAnalysisIndexSelect');
        const marketAnalysisProgress = document.getElementById('marketAnalysisProgress');
        const marketAnalysisProgressText = document.getElementById('marketAnalysisProgressText');
        const marketPredictResultContent = document.getElementById('marketPredictResultContent');
        const marketPredictRunBtn = document.getElementById('marketPredictRunBtn');
        const marketPredictCustomDaysInput = document.getElementById('marketPredictCustomDaysInput');
        const marketPredictDayButtons = document.querySelectorAll('.market-predict-day-option');

        const marketMeta = document.getElementById('marketMeta');
        const marketStatus = document.getElementById('marketStatus');
        const indexCards = document.getElementById('indexCards');
        const marketPrimaryGrid = document.getElementById('marketPrimaryGrid');
        const marketChartCard = document.getElementById('marketChartCard');
        const marketExtraGrid = document.getElementById('marketExtraGrid');
        const marketIndicatorStrip = document.getElementById('marketIndicatorStrip');
        const marketMaLegend = document.getElementById('marketMaLegend');
        const chartShell = document.getElementById('chartShell');
        const chartTitle = document.getElementById('chartTitle');
        const chartSubtitle = document.getElementById('chartSubtitle');
        const chartLatest = document.getElementById('chartLatest');
        const chartChange = document.getElementById('chartChange');
        const chartStartDate = document.getElementById('chartStartDate');
        const chartEndDate = document.getElementById('chartEndDate');
        const chartMinValue = document.getElementById('chartMinValue');
        const chartMaxValue = document.getElementById('chartMaxValue');
        const reloadMarketBtn = document.getElementById('reloadMarketBtn');
        const chartPeriodButtons = document.querySelectorAll('.chart-period-btn');
        const marketRefreshInterval = document.getElementById('marketRefreshInterval');
        const marketVolumeShell = document.getElementById('marketVolumeShell');
        const marketRsiShell = document.getElementById('marketRsiShell');
        const marketMacdShell = document.getElementById('marketMacdShell');

        const sectorPickerInput = document.getElementById('sectorPickerInput');
        const sectorSelect = document.getElementById('sectorSelect');
        const sectorSearchBtn = document.getElementById('sectorSearchBtn');
        const sectorResetBtn = document.getElementById('sectorResetBtn');
        const sectorMeta = document.getElementById('sectorMeta');
        const sectorStatus = document.getElementById('sectorStatus');
        const sectorTableWrap = document.getElementById('sectorTableWrap');
        const sectorBody = document.getElementById('sectorBody');
        const sectorPagination = document.getElementById('sectorPagination');
        const sectorOptionsList = document.getElementById('sectorOptionsList');

        const stockSearchInput = document.getElementById('stockSearchInput');
        const stockDirectoryFavoriteSelect = document.getElementById('stockDirectoryFavoriteSelect');
        const stockSearchBtn = document.getElementById('stockSearchBtn');
        const stockDirectoryMeta = document.getElementById('stockDirectoryMeta');
        const stockDirectoryStatus = document.getElementById('stockDirectoryStatus');
        const stockDirectoryTableWrap = document.getElementById('stockDirectoryTableWrap');
        const stockDirectoryBody = document.getElementById('stockDirectoryBody');
        const stockDirectoryPagination = document.getElementById('stockDirectoryPagination');
        const stockChartCard = document.getElementById('stockChartCard');
        const stockChartTitle = document.getElementById('stockChartTitle');
        const stockChartSubtitle = document.getElementById('stockChartSubtitle');
        const stockChartLatest = document.getElementById('stockChartLatest');
        const stockChartChange = document.getElementById('stockChartChange');
        const stockChartShell = document.getElementById('stockChartShell');
        const stockChartStartDate = document.getElementById('stockChartStartDate');
        const stockChartEndDate = document.getElementById('stockChartEndDate');
        const stockChartMinValue = document.getElementById('stockChartMinValue');
        const stockChartMaxValue = document.getElementById('stockChartMaxValue');
        const stockChartTypeButtons = document.querySelectorAll('.stock-chart-type-btn');
        const stockChartRangeButtons = document.querySelectorAll('.stock-chart-range-btn');
        const stockMenuToggle = document.getElementById('stockMenuToggle');
        const stockSubmenu = document.getElementById('stockSubmenu');
        const stockSubmenuItems = document.querySelectorAll('.submenu-item');
        const stockRefreshInterval = document.getElementById('stockRefreshInterval');
        const stockGainersList = document.getElementById('stockGainersList');
        const stockLosersList = document.getElementById('stockLosersList');
        const stockRankingMeta = document.getElementById('stockRankingMeta');
        const favoriteDashboardMeta = document.getElementById('favoriteDashboardMeta');
        const favoriteSnapshotBody = document.getElementById('favoriteSnapshotBody');
        const favoritePieShell = document.getElementById('favoritePieShell');
        const favoriteBarsShell = document.getElementById('favoriteBarsShell');
        const profileUsernameInput = document.getElementById('profileUsernameInput');
        const profileAvatarInput = document.getElementById('profileAvatarInput');
        const profileAvatarPreview = document.getElementById('profileAvatarPreview');
        const saveProfileBtn = document.getElementById('saveProfileBtn');
        const profileStatus = document.getElementById('profileStatus');
        const reportEmailInput = document.getElementById('reportEmailInput');
        const saveReportEmailBtn = document.getElementById('saveReportEmailBtn');
        const reportEmailStatus = document.getElementById('reportEmailStatus');
        const reportScheduleEnabledInput = document.getElementById('reportScheduleEnabledInput');
        const reportScheduleTimeInput = document.getElementById('reportScheduleTimeInput');
        const reportScheduleStockList = document.getElementById('reportScheduleStockList');
        const saveReportScheduleBtn = document.getElementById('saveReportScheduleBtn');
        const reportScheduleStatus = document.getElementById('reportScheduleStatus');
        const llmSystemPromptInput = document.getElementById('llmSystemPromptInput');
        const llmUserPromptInput = document.getElementById('llmUserPromptInput');
        const saveLlmPromptsBtn = document.getElementById('saveLlmPromptsBtn');
        const llmPromptStatus = document.getElementById('llmPromptStatus');
        const settingsAddStockCodeInput = document.getElementById('settingsAddStockCodeInput');
        const settingsAddStockNameInput = document.getElementById('settingsAddStockNameInput');
        const settingsAddStockBtn = document.getElementById('settingsAddStockBtn');
        const settingsStockAlert = document.getElementById('settingsStockAlert');
        const settingsStockList = document.getElementById('settingsStockList');
        const settingsStockToggleBtn = document.getElementById('settingsStockToggleBtn');
        const settingsStockToggleMeta = document.getElementById('settingsStockToggleMeta');
        const riskPreferenceSlider = document.getElementById('riskPreferenceSlider');
        const riskPreferenceThumb = document.getElementById('riskPreferenceThumb');
        const riskPreferenceValue = document.getElementById('riskPreferenceValue');
        const sentimentMeta = document.getElementById('sentimentMeta');
        const sentimentStatus = document.getElementById('sentimentStatus');
        const sentimentList = document.getElementById('sentimentList');
        const sentimentPagination = document.getElementById('sentimentPagination');
        const sentimentTabs = document.querySelectorAll('.sentiment-tab');
        const sentimentMarketFilters = document.getElementById('sentimentMarketFilters');
        const sentimentSectorFilters = document.getElementById('sentimentSectorFilters');
        const sentimentStockFilters = document.getElementById('sentimentStockFilters');
        const sentimentStartTimeInput = document.getElementById('sentimentStartTimeInput');
        const sentimentEndTimeInput = document.getElementById('sentimentEndTimeInput');
        const sentimentSectorStartTimeInput = document.getElementById('sentimentSectorStartTimeInput');
        const sentimentSectorEndTimeInput = document.getElementById('sentimentSectorEndTimeInput');
        const sentimentStockStartTimeInput = document.getElementById('sentimentStockStartTimeInput');
        const sentimentStockEndTimeInput = document.getElementById('sentimentStockEndTimeInput');
        const sentimentSectorSelect = document.getElementById('sentimentSectorSelect');
        const sentimentSectorInput = document.getElementById('sentimentSectorInput');
        const sentimentStockCodeInput = document.getElementById('sentimentStockCodeInput');
        const sentimentFavoriteStockSelect = document.getElementById('sentimentFavoriteStockSelect');
        const loadMarketSentimentBtn = document.getElementById('loadMarketSentimentBtn');
        const loadSectorSentimentBtn = document.getElementById('loadSectorSentimentBtn');
        const loadStockSentimentBtn = document.getElementById('loadStockSentimentBtn');
        const loadAllFavoriteSentimentBtn = document.getElementById('loadAllFavoriteSentimentBtn');
        const predictDetailLink = document.getElementById('predictDetailLink');
        const themeToggleBtn = document.getElementById('themeToggleBtn');
        const sidebarClockTime = document.getElementById('sidebarClockTime');
        const modelInfoPage = document.getElementById('modelInfoPage');
        const modelInfoNav = document.getElementById('modelInfoNav');
        const forumMeta = document.getElementById('forumMeta');
        const forumComposerMeta = document.getElementById('forumComposerMeta');
        const forumPostContent = document.getElementById('forumPostContent');
        const forumPostSubmitBtn = document.getElementById('forumPostSubmitBtn');
        const forumRefreshBtn = document.getElementById('forumRefreshBtn');
        const forumSortSelect = document.getElementById('forumSortSelect');
        const forumStatus = document.getElementById('forumStatus');
        const forumList = document.getElementById('forumList');
        const forumTabs = document.querySelectorAll('.forum-tab');
        const forumComposePanel = document.getElementById('forumComposePanel');
        const forumFeedPanel = document.getElementById('forumFeedPanel');
        const forumImageInput = document.getElementById('forumImageInput');
        const forumImagePreview = document.getElementById('forumImagePreview');
        const forumImagePreviewImg = document.getElementById('forumImagePreviewImg');

        const menuItems = document.querySelectorAll('.menu-item');
        const panels = document.querySelectorAll('.panel');

        const marketState = { data: null, activeKey: null, rangeDays: 365 };
        const stockDirectoryState = { keyword: '', page: 1 };
        const stockChartState = { activeCode: '', activeName: '', activeType: 'candlestick', data: null, rangeDays: 365 };
        const sectorState = { loaded: false, selectedSector: '', selectedSectorCode: '', keyword: '', page: 1 };
        const settingsState = { loaded: false, stocksLoaded: false, stockListExpanded: false, reportScheduleSelectedCodes: [] };
        const generatedReportState = {};
        const sentimentState = {
            mode: 'market',
            sectorOptionsLoaded: false,
            currentItems: [],
            page: 1,
            pageSize: 10,
            marketTimer: null,
            requestToken: 0,
            cache: { market: null, sector: null, stock: null },
            initialAutoLoaded: false
        };
        const authState = { mode: 'login' };
        const forumState = { loaded: false, items: [], sortBy: 'created_at' };
        const autoRefreshState = {
            marketTimer: null,
            stockTimer: null,
            rankingTimer: null,
            marketLoading: false,
            stockLoading: false
        };
        const STOCK_RANKING_REFRESH_MS = 10 * 60 * 1000;
        const THEME_STORAGE_KEY = 'stockllm-theme';
        const RISK_PREFERENCE_STORAGE_KEY = 'stockllm-risk-preference';
        const RISK_PREFERENCE_OPTIONS = [
            { level: 1, label: '激进' },
            { level: 2, label: '偏激进' },
            { level: 3, label: '平和' },
            { level: 4, label: '偏保守' },
            { level: 5, label: '保守' }
        ];
        let selectedPredictDays = 1;
        let selectedMarketPredictDays = 1;
        const predictCustomDaysInput = document.getElementById('predictCustomDaysInput');
        const MODEL_INFO_ITEMS = [
            {
                title: 'MA 均线',
                category: '技术指标',
                role: '判断价格趋势骨架是否偏强',
                chart: '短中长期均线关系图',
                signal: '短期均线在中长期均线上方通常偏多，均线反复交错则偏震荡。',
                focus: '看 MA5、MA10、MA20 的排列顺序、均线间距和价格是否站稳均线。',
                strength: '解释直观，适合快速识别趋势方向，也便于和 K 线走势互相印证。',
                caution: '横盘震荡时假信号会增多，需要结合成交量和动量指标一起判断。'
            },
            {
                title: 'RSI',
                category: '技术指标',
                role: '识别短线过热、超跌和潜在反转',
                chart: '超买超卖摆动区间图',
                signal: '高位区域提示过热风险，低位区域提示超跌修复可能。',
                focus: '看 RSI 所处区间、近期拐头方向，以及是否进入高低位敏感区域。',
                strength: '对短期情绪波动很敏感，适合辅助判断追高或恐慌杀跌是否过度。',
                caution: '单边强趋势中可能长时间停留在高位或低位，不能脱离趋势背景单独使用。'
            },
            {
                title: 'MACD',
                category: '技术指标',
                role: '观察趋势动量增强、减弱或切换',
                chart: 'DIF/DEA 柱体图',
                signal: '金叉、死叉、零轴位置和柱体变化共同反映动量状态。',
                focus: '看 DIF 与 DEA 的相对位置、柱体是放大还是缩小，以及是否靠近零轴。',
                strength: '同时覆盖趋势和动量，适合中短期节奏确认。',
                caution: '本质上有滞后性，对突发波动响应较慢，更适合作为确认工具。'
            },
            {
                title: '趋势判断',
                category: '趋势结构',
                role: '归纳短中期行情方向和持续性',
                chart: '20日/60日斜率对比图',
                signal: '短中期斜率同向更有利于趋势延续，斜率分化则说明结构不够统一。',
                focus: '看 20 日与 60 日价格斜率、价格中心是否抬升，以及回撤是否可控。',
                strength: '提供总览判断，能把多个价格变化压缩成清晰的结构结论。',
                caution: '对盘中急变和消息驱动的短时反转不敏感。'
            },
            {
                title: 'Bollinger Bands',
                category: '波动结构',
                role: '判断价格偏离程度和波动率切换',
                chart: '布林带上下轨包络图',
                signal: '价格贴近上轨代表偏强或过热，贴近下轨代表偏弱或超跌；带宽变化反映波动扩张或收缩。',
                focus: '看价格在上中下轨的位置、带宽是否扩大，以及是否出现收口后放大的信号。',
                strength: '适合震荡市和波动率切换分析，也能补充风险解释。',
                caution: '强趋势里价格贴轨不一定立刻反转，需要结合趋势指标确认。'
            },
            {
                title: 'ADX',
                category: '趋势结构',
                role: '衡量趋势强弱而不是直接判断涨跌',
                chart: 'ADX 与 DI 指标图',
                signal: 'ADX 越高代表趋势越明确，+DI 与 -DI 的相对位置提供方向参考。',
                focus: '看 ADX 数值高低、+DI 是否强于 -DI，以及趋势强度是否持续改善。',
                strength: '适合作为趋势过滤器，回答当前信号是否值得跟随。',
                caution: '对短线拐点不敏感，不能当作独立买卖信号。'
            },
            {
                title: 'ARIMA',
                category: '时序预测',
                role: '基于历史价格序列外推短期走势',
                chart: '时间序列预测曲线',
                signal: '预测价格上移偏多，下移偏空，横向变化说明方向优势不明显。',
                focus: '看预测曲线方向、预测幅度和近期实际价格是否与模型假设一致。',
                strength: '逻辑清晰，适合作为时间序列基准模型，能够给出直观价格参考。',
                caution: '更适合相对平稳的序列，对突发事件和复杂非线性关系适应有限。'
            },
            {
                title: '波动率分类',
                category: '风险解释',
                role: '识别当前处于低、中、高波动环境',
                chart: '年化波动率分位图',
                signal: '高波动提示风险释放剧烈，低波动提示行情可能等待方向选择。',
                focus: '看近期波动率所处分位、是否明显抬升，以及与趋势信号是否匹配。',
                strength: '能解释同样的趋势信号在不同风险环境下为什么要采用不同节奏。',
                caution: '只描述风险状态，不直接给出涨跌方向。'
            },
            {
                title: 'Random Forest',
                category: '机器学习',
                role: '通过多棵决策树投票估计涨跌概率',
                chart: '特征重要性柱状图',
                signal: '上涨概率越高代表模型越偏多，同时可参考重要特征来自哪里。',
                focus: '看上涨概率、方向信号和特征重要性是否与技术指标结论一致。',
                strength: '稳健、抗噪声能力较好，能够处理非线性特征关系。',
                caution: '解释性弱于规则指标，模型质量受样本规模和标签构造影响较大。'
            },
            {
                title: 'XGBoost',
                category: '机器学习',
                role: '学习多维特征交互并输出方向概率',
                chart: 'Boosting 特征增益图',
                signal: '上涨或下跌概率体现短期方向优势，特征增益反映模型主要依据。',
                focus: '看概率优势是否足够明显，以及价格、动量、均线偏离、波动率等特征的贡献。',
                strength: '擅长捕捉复杂非线性关系，是补充传统指标的重要预测模块。',
                caution: '依赖样本质量和参数设置，市场环境明显切换时历史经验可能失效。'
            },
            {
                title: '线性回归',
                category: '趋势结构',
                role: '用趋势直线估计近期价格延伸方向',
                chart: '趋势拟合直线图',
                signal: '拟合斜率向上偏多，向下偏空，接近水平代表趋势延续性不足。',
                focus: '看拟合斜率、价格围绕趋势线的偏离程度，以及预测延伸是否稳定。',
                strength: '非常容易解释，适合作为判断趋势斜率的基准视角。',
                caution: '只能刻画线性趋势，对弯折、震荡和突发波动适应较弱。'
            }
        ];
        const MODEL_INFO_PRIORITY = ['MA 均线', 'MACD', 'RSI', 'ARIMA', 'XGBoost'];
        MODEL_INFO_ITEMS.sort((left, right) => {
            const leftIndex = MODEL_INFO_PRIORITY.indexOf(left.title);
            const rightIndex = MODEL_INFO_PRIORITY.indexOf(right.title);
            const normalizedLeft = leftIndex === -1 ? MODEL_INFO_PRIORITY.length : leftIndex;
            const normalizedRight = rightIndex === -1 ? MODEL_INFO_PRIORITY.length : rightIndex;
            return normalizedLeft - normalizedRight;
        });
        let currentModelInfoIndex = 0;

        function applyTheme(theme) {
            const isNight = theme === 'night';
            document.body.classList.toggle('theme-night', isNight);
            themeToggleBtn.setAttribute('aria-pressed', isNight ? 'true' : 'false');
        }

        function initTheme() {
            const savedTheme = localStorage.getItem(THEME_STORAGE_KEY);
            applyTheme(savedTheme === 'night' ? 'night' : 'day');
        }

        function toggleTheme() {
            const nextTheme = document.body.classList.contains('theme-night') ? 'day' : 'night';
            applyTheme(nextTheme);
            localStorage.setItem(THEME_STORAGE_KEY, nextTheme);
        }

        function getCurrentUserId() {
            return currentUser && currentUser.id ? currentUser.id : null;
        }

        function getUserInitial(user) {
            const name = user && user.username ? String(user.username) : '--';
            return name.slice(0, 1).toUpperCase();
        }

        function renderUserAvatar(container, user, extraClass = '') {
            if (!container) {
                return;
            }
            const avatarUrl = user && user.avatar_url ? user.avatar_url : '';
            if (avatarUrl) {
                container.innerHTML = `<img class="${extraClass}" src="${escapeHtmlAttribute(avatarUrl)}" alt="${escapeHtmlAttribute((user && user.username) || '用户头像')}">`;
            } else {
                container.textContent = getUserInitial(user);
            }
        }

        function setAuthStatus(message, type = 'default') {
            authStatus.textContent = message;
            authStatus.className = 'settings-status';
            if (type === 'success') {
                authStatus.classList.add('success');
            }
            if (type === 'error') {
                authStatus.classList.add('error');
            }
        }

        function updateUserUi() {
            if (currentUser) {
                sidebarUsername.textContent = currentUser.username;
                sidebarUserMeta.textContent = `UUID ${currentUser.uuid} ${currentUser.is_admin ? '· 管理员' : ''}`;
                renderUserAvatar(sidebarUserAvatar, currentUser);
                renderUserAvatar(profileAvatarPreview, currentUser);
                if (profileUsernameInput) {
                    profileUsernameInput.value = currentUser.username || '';
                }
                authOverlay.style.display = 'none';
                if (userManageMenuItem) {
                    userManageMenuItem.style.display = currentUser.is_admin ? 'block' : 'none';
                }
                adminUsersCard.style.display = currentUser.is_admin ? 'block' : 'none';
            } else {
                sidebarUsername.textContent = '未登录';
                sidebarUserMeta.textContent = 'UUID --';
                renderUserAvatar(sidebarUserAvatar, null);
                renderUserAvatar(profileAvatarPreview, null);
                authOverlay.style.display = 'flex';
                if (userManageMenuItem) {
                    userManageMenuItem.style.display = 'none';
                }
                adminUsersCard.style.display = 'none';
            }
            if (forumComposerMeta) {
                forumComposerMeta.textContent = currentUser ? `当前登录用户：${currentUser.username}（UUID ${currentUser.uuid}），发帖后会自动记录时间戳。` : '登录后可直接发帖，系统会自动带上用户名和时间戳。';
            }
        }

        function persistCurrentUser(user) {
            currentUser = user || null;
            if (currentUser) {
                localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(currentUser));
            } else {
                localStorage.removeItem(USER_STORAGE_KEY);
            }
            updateUserUi();
        }

        async function initAuthState() {
            try {
                const saved = localStorage.getItem(USER_STORAGE_KEY);
                currentUser = saved ? JSON.parse(saved) : null;
                if (currentUser) {
                    const response = await fetch(`${BASE_API_URL}/auth/me`);
                    const result = await response.json();
                    if (result.code !== 200 || !result.data?.user) {
                        throw new Error(result.msg || '登录会话已失效');
                    }
                    currentUser = result.data.user;
                    localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(currentUser));
                }
            } catch (error) {
                currentUser = null;
                localStorage.removeItem(USER_STORAGE_KEY);
            }
            updateUserUi();
            setAuthMode(authState.mode);
        }

        function setAuthMode(mode) {
            authState.mode = ['login', 'register', 'forgot'].includes(mode) ? mode : 'login';
            const isRegister = authState.mode === 'register';
            const isForgot = authState.mode === 'forgot';
            authStatusText.textContent = isForgot
                ? '输入账号/UUID 与注册邮箱，验证后重新设置登录密码。'
                : authState.mode === 'login'
                    ? '登录支持账号、邮箱或 UUID 三种方式。'
                    : '注册时需完成邮箱验证，提交后等待管理员审核。';
            authSubmitBtn.textContent = isForgot ? '重置密码' : authState.mode === 'login' ? '立即登录' : '立即注册';
            authSwitchBtn.textContent = authState.mode === 'login' ? '注册' : '返回登录';
            authForgotBtn.style.display = authState.mode === 'login' ? 'inline-flex' : 'none';
            authUsernameInput.placeholder = isForgot ? '请输入账号或 UUID' : isRegister ? '请输入账号' : '请输入账号/邮箱/UUID';
            authUsernameInput.style.display = 'block';
            authEmailInput.placeholder = isForgot ? '请输入注册邮箱' : '注册时请输入邮箱';
            authEmailInput.style.display = (isRegister || isForgot) ? 'block' : 'none';
            authCodeRow.style.display = (isRegister || isForgot) ? 'grid' : 'none';
            authEmailCodeInput.placeholder = isForgot ? '请输入找回密码验证码' : '请输入邮箱验证码';
            sendEmailCodeBtn.textContent = isForgot ? '获取验证码' : '获取验证码';
            authPasswordInput.placeholder = isForgot ? '请输入新密码' : '请输入密码';
            if (!isRegister && !isForgot) {
                authEmailInput.value = '';
                authEmailCodeInput.value = '';
            }
            if (isForgot) {
                authUsernameInput.value = '';
            }
            setAuthStatus('');
        }

        async function sendAuthEmailCode() {
            const email = authEmailInput.value.trim();
            if (!email) {
                setAuthStatus(authState.mode === 'forgot' ? '请输入注册邮箱后再获取验证码。' : '请输入注册邮箱后再获取验证码。', 'error');
                return;
            }
            setAuthStatus('正在发送邮箱验证码...');
            sendEmailCodeBtn.disabled = true;
            try {
                const purpose = authState.mode === 'forgot' ? 'password_reset' : 'register';
                const response = await fetch(`${BASE_API_URL}/auth/send_email_code`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, purpose }),
                });
                const result = await response.json();
                if (result.code !== 200) {
                    throw new Error(result.msg);
                }
                setAuthStatus('邮箱验证码已发送，请注意查收。', 'success');
            } catch (error) {
                setAuthStatus(error.message, 'error');
            } finally {
                window.setTimeout(() => {
                    sendEmailCodeBtn.disabled = false;
                }, 1000);
            }
        }

        async function submitAuth() {
            const username = authUsernameInput.value.trim();
            const password = authPasswordInput.value.trim();
            const email = authEmailInput.value.trim();
            const emailCode = authEmailCodeInput.value.trim();
            if (authState.mode === 'forgot') {
                if (!username || !email || !emailCode || !password) {
                    setAuthStatus('请填写账号/UUID、注册邮箱、验证码和新密码。', 'error');
                    return;
                }
                setAuthStatus('正在重置密码...');
                try {
                    const response = await fetch(`${BASE_API_URL}/auth/reset_password`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ username, email, email_code: emailCode, password }),
                    });
                    const result = await response.json();
                    if (result.code !== 200) {
                        throw new Error(result.msg);
                    }
                    authPasswordInput.value = '';
                    authEmailCodeInput.value = '';
                    setAuthStatus(result.msg, 'success');
                    window.setTimeout(() => {
                        setAuthMode('login');
                        setAuthStatus('密码已重置，请使用新密码登录。', 'success');
                    }, 900);
                } catch (error) {
                    setAuthStatus(error.message, 'error');
                }
                return;
            }
            if (!username || !password) {
                setAuthStatus(authState.mode === 'login' ? '请输入账号/邮箱/UUID 和密码。' : '请输入账号和密码。', 'error');
                return;
            }
            if (authState.mode === 'register' && /^\d{1,3}$/.test(username)) {
                setAuthStatus('账号不能是一位、两位或三位纯数字。', 'error');
                return;
            }
            if (authState.mode === 'register' && (!email || !emailCode)) {
                setAuthStatus('注册时请填写邮箱并输入验证码。', 'error');
                return;
            }
            const endpoint = authState.mode === 'register' ? 'register' : 'login';
            setAuthStatus(authState.mode === 'register' ? '正在注册...' : '正在登录...');
            try {
                const response = await fetch(`${BASE_API_URL}/auth/${endpoint}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password, email, email_code: emailCode }),
                });
                const result = await response.json();
                if (result.code !== 200) {
                    throw new Error(result.msg);
                }
                if (authState.mode === 'register') {
                    authPasswordInput.value = '';
                    authEmailCodeInput.value = '';
                    setAuthStatus(result.msg || '注册申请已提交，请等待管理员审核后登录。', 'success');
                    window.setTimeout(() => {
                        setAuthMode('login');
                        setAuthStatus('注册申请已提交，请等待管理员审核后登录。', 'success');
                    }, 900);
                    return;
                }
                persistCurrentUser(result.data.user || null);
                authPasswordInput.value = '';
                authEmailCodeInput.value = '';
                setAuthStatus(result.msg, 'success');
                await bootstrapAuthedData();
                switchPanel('marketPanel');
            } catch (error) {
                setAuthStatus(error.message, 'error');
            }
        }

        async function logout() {
            try {
                await fetch(`${BASE_API_URL}/auth/logout`, { method: 'POST' });
            } finally {
                persistCurrentUser(null);
            }
            Object.keys(generatedReportState).forEach(key => delete generatedReportState[key]);
            historyReportContent.innerHTML = '';
            if (historyReportStandaloneContent) {
                historyReportStandaloneContent.innerHTML = '';
            }
            favoriteSnapshotBody.innerHTML = '';
            favoritePieShell.innerHTML = '';
            favoriteBarsShell.innerHTML = '';
            sentimentState.initialAutoLoaded = false;
            sentimentState.cache = { market: null, sector: null, stock: null };
            switchPanel('marketPanel');
        }

        function startAnalysisProgress() {
            if (!analysisProgress) {
                return;
            }
            analysisProgress.style.display = 'block';
            analysisProgressText.textContent = '正在生成 LLM 报告...';
        }

        function stopAnalysisProgress(success = true) {
            if (!analysisProgress) {
                return;
            }
            if (success) {
                analysisProgressText.textContent = 'LLM 报告生成完成';
            } else {
                analysisProgressText.textContent = 'LLM 报告生成失败';
            }
            window.setTimeout(() => {
                analysisProgress.style.display = 'none';
            }, 900);
        }

        function buildPieChartSvg(items, width = 320, height = 260) {
            const validItems = (items || []).filter(item => Number(item.value || 0) > 0);
            if (!validItems.length) {
                return '<div class="chart-empty">暂无可展示数据。</div>';
            }
            const radius = 84;
            const centerX = 110;
            const centerY = 120;
            const total = validItems.reduce((sum, item) => sum + Number(item.value || 0), 0);
            let currentAngle = -Math.PI / 2;
            const slices = validItems.map(item => {
                const value = Number(item.value || 0);
                const sweep = (value / total) * Math.PI * 2;
                const nextAngle = currentAngle + sweep;
                const x1 = centerX + radius * Math.cos(currentAngle);
                const y1 = centerY + radius * Math.sin(currentAngle);
                const x2 = centerX + radius * Math.cos(nextAngle);
                const y2 = centerY + radius * Math.sin(nextAngle);
                const largeArc = sweep > Math.PI ? 1 : 0;
                const path = `M ${centerX} ${centerY} L ${x1.toFixed(2)} ${y1.toFixed(2)} A ${radius} ${radius} 0 ${largeArc} 1 ${x2.toFixed(2)} ${y2.toFixed(2)} Z`;
                currentAngle = nextAngle;
                return `<path d="${path}" fill="${item.color || '#2563eb'}" opacity="0.92"></path>`;
            }).join('');
            const legends = validItems.map((item, index) => `
                <div class="pie-legend-item" style="top:${18 + index * 28}px">
                    <span class="pie-legend-dot" style="background:${item.color || '#2563eb'}"></span>
                    <span>${item.label}</span>
                    <strong>${item.value}</strong>
                </div>
            `).join('');
            return `
                <div class="pie-chart-wrap">
                    <svg class="chart-svg" viewBox="0 0 ${width} ${height}" preserveAspectRatio="xMidYMid meet">
                        ${slices}
                        <circle cx="${centerX}" cy="${centerY}" r="42" fill="#ffffff" opacity="0.95"></circle>
                        <text x="${centerX}" y="${centerY - 4}" text-anchor="middle" font-size="14" fill="#64748b">总计</text>
                        <text x="${centerX}" y="${centerY + 18}" text-anchor="middle" font-size="22" font-weight="700" fill="#0f172a">${total}</text>
                    </svg>
                    <div class="pie-legends">${legends}</div>
                </div>
            `;
        }

        function renderModelInfoPage() {
            const item = MODEL_INFO_ITEMS[currentModelInfoIndex];
            if (!item || !modelInfoPage) {
                return;
            }
            if (modelInfoNav) {
                modelInfoNav.innerHTML = MODEL_INFO_ITEMS.map((navItem, index) => `
                    <button type="button" class="model-info-nav-item ${index === currentModelInfoIndex ? 'active' : ''}" data-index="${index}">
                        <span class="model-info-nav-category">${navItem.category}</span>
                        <strong>${navItem.title}</strong>
                    </button>
                `).join('');
            }
            modelInfoPage.innerHTML = `
                <div class="model-info-page-head">
                    <div>
                        <div class="model-info-kicker">${item.category}</div>
                        <div class="model-info-title">${item.title}</div>
                        <p class="model-info-role">${item.role}</p>
                    </div>
                    <div class="model-info-chart-card">
                        <span>图表示意</span>
                        <strong>${item.chart}</strong>
                    </div>
                </div>
                <div class="model-info-diagram" aria-hidden="true">
                    <div class="model-info-diagram-axis"></div>
                    <div class="model-info-diagram-wave"></div>
                    <div class="model-info-diagram-line"></div>
                </div>
                <div class="model-info-grid">
                    <div class="model-info-note model-info-note-primary">
                        <span>信号怎么看</span>
                        <p>${item.signal}</p>
                    </div>
                    <div class="model-info-note">
                        <span>重点关注</span>
                        <p>${item.focus}</p>
                    </div>
                    <div class="model-info-note">
                        <span>优势</span>
                        <p>${item.strength}</p>
                    </div>
                    <div class="model-info-note model-info-note-warn">
                        <span>局限提醒</span>
                        <p>${item.caution}</p>
                    </div>
                </div>
            `;
        }

        async function loadAdminUsers() {
            if (!currentUser || !currentUser.is_admin) {
                adminUsersCard.style.display = 'none';
                return;
            }
            try {
                const response = await fetch(`${BASE_API_URL}/users?user_id=${getCurrentUserId()}`);
                const result = await response.json();
                if (result.code !== 200) {
                    throw new Error(result.msg);
                }
                const statusLabels = {
                    pending: '待审核',
                    approved: '已通过',
                };
                adminUsersBody.innerHTML = (result.data.items || []).map(item => `
                    <tr>
                        <td>${item.id}</td>
                        <td>${item.uuid}</td>
                        <td>${item.username}</td>
                        <td>${item.email || '--'}</td>
                        <td>${item.is_admin ? '管理员' : '普通用户'}</td>
                        <td>${statusLabels[item.approval_status] || item.approval_status || '已通过'}</td>
                        <td>${formatInteger(item.token_usage || 0)}</td>
                        <td>
                            ${(!item.is_admin && item.approval_status === 'pending') ? `<button type="button" class="table-action-btn approve-user-btn" data-user-id="${item.id}" data-username="${escapeHtmlAttribute(item.username)}">通过</button>` : ''}
                            ${item.is_admin ? '<span class="table-action-disabled">不可注销</span>' : `<button type="button" class="table-action-btn delete-user-btn" data-user-id="${item.id}" data-username="${escapeHtmlAttribute(item.username)}">注销</button>`}
                        </td>
                    </tr>
                `).join('');
                adminUsersCard.style.display = 'block';
            } catch (error) {
                adminUsersBody.innerHTML = `<tr><td colspan="8">${error.message}</td></tr>`;
                adminUsersCard.style.display = 'block';
            }
        }

        async function approveUserAccount(userId, username) {
            if (!currentUser || !currentUser.is_admin) {
                return;
            }
            if (!confirm(`确定通过用户 ${username} 的注册申请吗？`)) {
                return;
            }
            try {
                const response = await fetch(`${BASE_API_URL}/users/${userId}/approve`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_id: getCurrentUserId() }),
                });
                const result = await response.json();
                if (result.code !== 200) {
                    throw new Error(result.msg);
                }
                await loadAdminUsers();
            } catch (error) {
                alert(`审核失败：${error.message}`);
            }
        }

        async function deleteUserAccount(userId, username) {
            if (!currentUser || !currentUser.is_admin) {
                return;
            }
            if (!confirm(`确定要注销用户 ${username} 吗？该操作会同时删除其自选股与历史报告。`)) {
                return;
            }
            try {
                const response = await fetch(`${BASE_API_URL}/users/${userId}?user_id=${getCurrentUserId()}`, {
                    method: 'DELETE',
                });
                const result = await response.json();
                if (result.code !== 200) {
                    throw new Error(result.msg);
                }
                await loadAdminUsers();
            } catch (error) {
                alert(`注销失败：${error.message}`);
            }
        }

        async function loadHistoryReports() {
            if (!getCurrentUserId()) {
                return;
            }
            try {
                const response = await fetch(`${BASE_API_URL}/report_histories?user_id=${getCurrentUserId()}`);
                const result = await response.json();
                if (result.code !== 200) {
                    throw new Error(result.msg);
                }
                const items = result.data.items || [];
                if (!items.length) {
                    const emptyHtml = '<p class="tip">当前还没有历史报告。</p>';
                    historyReportContent.innerHTML = emptyHtml;
                    if (historyReportStandaloneContent) {
                        historyReportStandaloneContent.innerHTML = emptyHtml;
                    }
                    return;
                }
                const historyHtml = items.map(item => `
                    <details class="history-report-item">
                        <summary>
                            <span class="history-report-summary-text">${item.created_at} · ${item.stock_code} ${item.stock_name || ''}</span>
                        </summary>
                        <div class="history-report-actions">
                            <a class="secondary-btn" href="${BASE_API_URL}/report_histories/${item.id}/download?user_id=${encodeURIComponent(String(getCurrentUserId()))}" download>下载 HTML 报告</a>
                        </div>
                        <div class="generated-report-preview">
                            <iframe title="${item.stock_code} 历史报告" srcdoc="${escapeHtmlAttribute(item.report_html || '')}"></iframe>
                        </div>
                    </details>
                `).join('');
                historyReportContent.innerHTML = historyHtml;
                if (historyReportStandaloneContent) {
                    historyReportStandaloneContent.innerHTML = historyHtml;
                }
            } catch (error) {
                const errorHtml = `<p class="alert-error">历史报告加载失败：${error.message}</p>`;
                historyReportContent.innerHTML = errorHtml;
                if (historyReportStandaloneContent) {
                    historyReportStandaloneContent.innerHTML = errorHtml;
                }
            }
        }

        async function loadFavoriteSnapshot() {
            if (!getCurrentUserId()) {
                return;
            }
            try {
                const response = await fetch(`${BASE_API_URL}/favorites_snapshot?user_id=${getCurrentUserId()}`);
                const result = await response.json();
                if (result.code !== 200) {
                    throw new Error(result.msg);
                }
                const data = result.data || {};
                favoriteDashboardMeta.textContent = `更新时间：${data.updated_at || '--'} | 来源：${data.source || '--'}${data.warning ? ` | 提示：${data.warning}` : ''}`;
                const items = data.items || [];
                favoriteSnapshotBody.innerHTML = items.length ? items.map(item => `
                    <tr>
                        <td>${item.code}</td>
                        <td>${item.name}</td>
                        <td>${formatValue(item.latest_price)}</td>
                        <td class="${getMarketTrendClass(Number(item.change_percent || 0))}">${formatValue(item.change_percent)}%</td>
                        <td>${formatInteger(item.volume)}</td>
                        <td>${formatYi(item.amount)}</td>
                    </tr>
                `).join('') : '<tr><td colspan="6">暂无自选股数据</td></tr>';
                favoritePieShell.innerHTML = buildPieChartSvg(data.distribution || []);
                const bars = (data.volume_amount_chart || []).slice(0, 8);
                favoriteBarsShell.innerHTML = bars.length ? bars.map(item => `
                    <div class="favorite-bar-item">
                        <div class="favorite-bar-label">${item.code}</div>
                        <div class="favorite-bar-track"><span style="width:${Math.min(100, ((item.amount || 0) / Math.max(...bars.map(bar => bar.amount || 1), 1)) * 100)}%"></span></div>
                        <div class="favorite-bar-value">${formatYi(item.amount)}</div>
                    </div>
                `).join('') : '<div class="chart-empty">暂无柱状图数据。</div>';
            } catch (error) {
                favoriteSnapshotBody.innerHTML = `<tr><td colspan="6">${error.message}</td></tr>`;
                favoritePieShell.innerHTML = '<div class="chart-empty">饼图加载失败。</div>';
                favoriteBarsShell.innerHTML = '<div class="chart-empty">柱状图加载失败。</div>';
            }
        }

        async function loadStockRankings() {
            try {
                const response = await fetch(`${BASE_API_URL}/stock_rankings?limit=8`);
                const result = await response.json();
                if (result.code !== 200) {
                    throw new Error(result.msg);
                }
                const data = result.data || {};
                stockRankingMeta.textContent = `更新时间：${data.updated_at || '--'} | 来源：${data.source || '--'}${data.warning ? ` | 提示：${data.warning}` : ''}`;
                stockGainersList.innerHTML = (data.gainers || []).map((item, index) => `
                    <div class="ranking-item">
                        <span class="ranking-order">${index + 1}</span>
                        <span class="ranking-name">${item.code} ${item.name}</span>
                        <strong class="market-up">${formatValue(item.change_percent)}%</strong>
                    </div>
                `).join('') || '<div class="chart-empty">暂无数据。</div>';
                stockLosersList.innerHTML = (data.losers || []).map((item, index) => `
                    <div class="ranking-item">
                        <span class="ranking-order">${index + 1}</span>
                        <span class="ranking-name">${item.code} ${item.name}</span>
                        <strong class="market-down">${formatValue(item.change_percent)}%</strong>
                    </div>
                `).join('') || '<div class="chart-empty">暂无数据。</div>';
            } catch (error) {
                stockRankingMeta.textContent = `排行榜加载失败：${error.message}`;
            }
        }

        async function bootstrapAuthedData() {
            if (!getCurrentUserId()) {
                return;
            }
            await Promise.all([
                loadManagedStocks(),
                loadReportEmailSettings(),
                loadLlmPromptSettings(),
                loadAdminUsers(),
                loadHistoryReports(),
                loadFavoriteSnapshot(),
                loadStockRankings()
            ]);
            autoLoadInitialSentiment();
        }

        function setManagedStocksExpanded(expanded) {
            settingsState.stockListExpanded = Boolean(expanded);
            settingsStockList.classList.toggle('collapsed', !settingsState.stockListExpanded);
            settingsStockToggleBtn.setAttribute('aria-expanded', settingsState.stockListExpanded ? 'true' : 'false');
            settingsStockToggleMeta.textContent = settingsState.stockListExpanded ? '点击收起' : '点击展开';
        }

        function setChartPeriod(period) {
            marketState.rangeDays = Number(period || 365);
            chartPeriodButtons.forEach(button => {
                button.classList.toggle('active', Number(button.dataset.range) === marketState.rangeDays);
            });
        }

        function setStockChartType(type) {
            stockChartState.activeType = ['candlestick', 'volume', 'compare'].includes(type) ? type : 'candlestick';
            stockChartTypeButtons.forEach(button => {
                button.classList.toggle('active', button.dataset.chartType === stockChartState.activeType);
            });
        }

        function setStockChartRange(days) {
            stockChartState.rangeDays = Number(days || 365);
            stockChartRangeButtons.forEach(button => {
                button.classList.toggle('active', Number(button.dataset.range) === stockChartState.rangeDays);
            });
        }

        function getSelectedCaseValues(selector) {
            return Array.from(document.querySelectorAll(selector)).filter(item => item.checked).map(item => item.value);
        }

        function getSelectedPredictCases() {
            const selected = getSelectedCaseValues('.predict-case-checkbox');
            return selected.length ? selected : ['ma', 'rsi', 'macd', 'arima', 'xgboost', 'trend', 'bollinger_bands', 'adx', 'volatility_classification', 'random_forest', 'linear_regression'];
        }

        function getSelectedMarketPredictCases() {
            const selected = getSelectedCaseValues('.market-predict-case-checkbox');
            return selected.length ? selected : ['ma', 'rsi', 'macd', 'arima', 'xgboost', 'trend', 'bollinger_bands', 'adx', 'volatility_classification', 'random_forest', 'linear_regression'];
        }

        function setSelectedPredictDays(days) {
            selectedPredictDays = Number(days || 1);
            document.querySelectorAll('.predict-day-option:not(.market-predict-day-option)').forEach(button => {
                button.classList.toggle('active', Number(button.dataset.days) === selectedPredictDays);
            });
            if (predictCustomDaysInput && ![1, 3, 7, 30, 60, 90, 120, 180].includes(selectedPredictDays)) {
                predictCustomDaysInput.value = String(selectedPredictDays);
            } else if (predictCustomDaysInput) {
                predictCustomDaysInput.value = '';
            }
        }

        function setSelectedMarketPredictDays(days) {
            selectedMarketPredictDays = Number(days || 1);
            marketPredictDayButtons.forEach(button => {
                button.classList.toggle('active', Number(button.dataset.days) === selectedMarketPredictDays);
            });
            if (marketPredictCustomDaysInput && ![1, 3, 7, 30, 60, 90, 120, 180].includes(selectedMarketPredictDays)) {
                marketPredictCustomDaysInput.value = String(selectedMarketPredictDays);
            } else if (marketPredictCustomDaysInput) {
                marketPredictCustomDaysInput.value = '';
            }
        }

        function padDateTimeNumber(value) {
            return String(value).padStart(2, '0');
        }

        function toDateTimeLocalValue(date, includeSeconds = false) {
            const current = date instanceof Date ? date : new Date();
            const datePart = `${current.getFullYear()}-${padDateTimeNumber(current.getMonth() + 1)}-${padDateTimeNumber(current.getDate())}`;
            const timePart = `${padDateTimeNumber(current.getHours())}:${padDateTimeNumber(current.getMinutes())}`;
            return includeSeconds ? `${datePart}T${timePart}:${padDateTimeNumber(current.getSeconds())}` : `${datePart}T${timePart}`;
        }

        function normalizeDateTimeLocalValue(value, defaultSeconds) {
            const trimmed = (value || '').trim();
            if (!trimmed) {
                return '';
            }
            const normalized = trimmed.replace('T', ' ');
            if (normalized.length === 16) {
                return `${normalized}:${defaultSeconds}`;
            }
            return normalized;
        }

        function formatClockTime(date) {
            const current = date instanceof Date ? date : new Date();
            return `${padDateTimeNumber(current.getHours())}:${padDateTimeNumber(current.getMinutes())}:${padDateTimeNumber(current.getSeconds())}`;
        }

        function escapeHtmlAttribute(value) {
            return String(value || '')
                .replace(/&/g, '&amp;')
                .replace(/"/g, '&quot;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;');
        }

        function escapeHtml(value) {
            return String(value || '')
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;')
                .replace(/'/g, '&#39;');
        }

        function buildLlmDebugBlock(reportContext) {
            const llmMeta = ((reportContext || {}).llm_meta) || {};
            const usage = llmMeta.usage || {};
            const debug = llmMeta.debug || {};
            const timing = llmMeta.timing_breakdown || {};
            const reportTiming = ((reportContext || {}).timing_breakdown) || {};
            const lines = [
                `LLM 状态：${llmMeta.status || '--'}`,
                `模型：${llmMeta.model || '--'}`,
                `联网：${llmMeta.enable_web_search === true ? '开启' : (llmMeta.enable_web_search === false ? '关闭' : '--')}`,
                `输入 Tokens：${usage.input_tokens ?? '--'}`,
                `输出 Tokens：${usage.output_tokens ?? '--'}`,
                `总 Tokens：${usage.total_tokens ?? '--'}`
            ];
            if (Object.keys(reportTiming).length) {
                lines.push(`报告阶段耗时：${JSON.stringify(reportTiming, null, 2)}`);
            }
            if (Object.keys(timing).length) {
                lines.push(`LLM 阶段耗时：${JSON.stringify(timing, null, 2)}`);
            }
            if (Array.isArray(debug.attempts) && debug.attempts.length) {
                lines.push(`LLM 重试明细：${JSON.stringify(debug.attempts, null, 2)}`);
            }
            if (debug.error) {
                lines.push(`失败原因：${debug.error}`);
            }
            if (debug.config_hint) {
                lines.push(`配置提示：${debug.config_hint}`);
            }
            if (debug.response_summary) {
                lines.push(`响应摘要：${typeof debug.response_summary === 'string' ? debug.response_summary : JSON.stringify(debug.response_summary, null, 2)}`);
            }
            if (debug.raw_response_preview) {
                lines.push(`原始返回预览：${debug.raw_response_preview}`);
            }
            return `
                <details class="debug-json-wrap">
                    <summary>LLM 调试信息</summary>
                    <pre>${escapeHtml(lines.join('\n\n'))}</pre>
                </details>
            `;
        }

        function parseSentimentRange(startInput, endInput, defaultDays) {
            const endValue = (endInput && endInput.value ? endInput.value : toDateTimeLocalValue(new Date(), true)).trim();
            const startValue = (startInput && startInput.value ? startInput.value : toDateTimeLocalValue(new Date(Date.now() - defaultDays * 24 * 60 * 60 * 1000))).trim();
            const startTime = normalizeDateTimeLocalValue(startValue, '00');
            const endTime = normalizeDateTimeLocalValue(endValue, '59');
            if (startTime && endTime && new Date(startTime.replace(' ', 'T')) > new Date(endTime.replace(' ', 'T'))) {
                throw new Error('起始时间不能晚于结束时间');
            }
            return { startTime, endTime };
        }

        function refreshSentimentEndTimes(now = new Date()) {
            const endValue = toDateTimeLocalValue(now, true);
            [sentimentEndTimeInput, sentimentSectorEndTimeInput, sentimentStockEndTimeInput].forEach(input => {
                if (!input) {
                    return;
                }
                input.value = endValue;
            });
        }

        function initSentimentDateRanges() {
            const now = new Date();
            const setRange = function(startInput, endInput, defaultHours) {
                if (!startInput || !endInput) {
                    return;
                }
                endInput.value = toDateTimeLocalValue(now, true);
                startInput.value = toDateTimeLocalValue(new Date(now.getTime() - defaultHours * 60 * 60 * 1000), true);
            };
            setRange(sentimentStartTimeInput, sentimentEndTimeInput, 3);
            setRange(sentimentSectorStartTimeInput, sentimentSectorEndTimeInput, 48);
            setRange(sentimentStockStartTimeInput, sentimentStockEndTimeInput, 24 * 7);
        }

        function syncMarketSentimentRange(now = new Date()) {
            if (!sentimentStartTimeInput || !sentimentEndTimeInput) {
                return;
            }
            sentimentEndTimeInput.value = toDateTimeLocalValue(now, true);
            sentimentStartTimeInput.value = toDateTimeLocalValue(new Date(now.getTime() - 3 * 60 * 60 * 1000), true);
        }

        function syncStockSentimentRange(now = new Date()) {
            if (!sentimentStockStartTimeInput || !sentimentStockEndTimeInput) {
                return;
            }
            sentimentStockEndTimeInput.value = toDateTimeLocalValue(now, true);
            sentimentStockStartTimeInput.value = toDateTimeLocalValue(new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000), true);
        }

        function updateSidebarClock(now = new Date()) {
            if (!sidebarClockTime) {
                return;
            }
            sidebarClockTime.textContent = formatClockTime(now);
        }

        function startRealtimeUiClock() {
            const syncNow = function() {
                const now = new Date();
                updateSidebarClock(now);
                refreshSentimentEndTimes(now);
            };
            syncNow();
            window.setInterval(syncNow, 1000);
        }

        function startMarketSentimentAutoRefresh() {
            if (sentimentState.marketTimer) {
                window.clearInterval(sentimentState.marketTimer);
            }
            sentimentState.marketTimer = window.setInterval(() => {
                if (sentimentState.mode === 'market') {
                    syncMarketSentimentRange();
                    loadMarketSentiment();
                }
            }, 5 * 60 * 1000);
        }

        function getRiskPointPosition(level) {
            const clampedLevel = Math.min(5, Math.max(1, Number(level || 3)));
            return 12 + (clampedLevel - 1) * 19;
        }

        function updateRiskPreference(level, persist = true) {
            const clampedLevel = Math.min(5, Math.max(1, Number(level || 3)));
            const selected = RISK_PREFERENCE_OPTIONS.find(option => option.level === clampedLevel) || RISK_PREFERENCE_OPTIONS[2];
            riskPreferenceThumb.style.left = `${getRiskPointPosition(clampedLevel)}%`;
            riskPreferenceValue.textContent = `当前：${selected.label}`;
            riskPreferenceSlider.setAttribute('aria-valuenow', String(clampedLevel));
            riskPreferenceSlider.setAttribute('aria-valuetext', selected.label);
            riskPreferenceSlider.dataset.level = String(clampedLevel);
            if (persist) {
                localStorage.setItem(RISK_PREFERENCE_STORAGE_KEY, String(clampedLevel));
            }
        }

        function getRiskPreferencePayload() {
            return String(Math.min(5, Math.max(1, Number(riskPreferenceSlider.dataset.level || 3))));
        }

        function setRiskPreferenceFromPointer(clientX) {
            const rect = riskPreferenceSlider.getBoundingClientRect();
            if (!rect.width) {
                return;
            }
            const ratio = Math.min(1, Math.max(0, (clientX - rect.left) / rect.width));
            const level = Math.min(5, Math.max(1, Math.round(ratio * 4) + 1));
            updateRiskPreference(level);
        }

        function initRiskPreference() {
            const savedLevel = Number(localStorage.getItem(RISK_PREFERENCE_STORAGE_KEY) || 3);
            updateRiskPreference(savedLevel, false);

            let dragging = false;
            const stopDragging = function() {
                dragging = false;
            };

            riskPreferenceSlider.addEventListener('pointerdown', function(event) {
                dragging = true;
                setRiskPreferenceFromPointer(event.clientX);
            });

            window.addEventListener('pointermove', function(event) {
                if (!dragging) {
                    return;
                }
                setRiskPreferenceFromPointer(event.clientX);
            });

            window.addEventListener('pointerup', stopDragging);
            window.addEventListener('pointercancel', stopDragging);

            riskPreferenceSlider.querySelectorAll('.risk-point').forEach(point => {
                point.addEventListener('click', function(event) {
                    event.stopPropagation();
                    updateRiskPreference(Number(this.dataset.level || 3));
                });
            });

            riskPreferenceSlider.addEventListener('keydown', function(event) {
                const currentLevel = Number(riskPreferenceSlider.dataset.level || 3);
                if (event.key === 'ArrowLeft' || event.key === 'ArrowDown') {
                    event.preventDefault();
                    updateRiskPreference(currentLevel - 1);
                }
                if (event.key === 'ArrowRight' || event.key === 'ArrowUp') {
                    event.preventDefault();
                    updateRiskPreference(currentLevel + 1);
                }
            });
        }

        function getRefreshIntervalMs(selectElement) {
            return Math.max(10, Number(selectElement.value || 30)) * 1000;
        }

        function startMarketAutoRefresh() {
            if (autoRefreshState.marketTimer) {
                window.clearInterval(autoRefreshState.marketTimer);
            }
            autoRefreshState.marketTimer = window.setInterval(() => {
                if (!autoRefreshState.marketLoading) {
                    loadMarketIndices({ silent: true });
                }
            }, getRefreshIntervalMs(marketRefreshInterval));
        }

        function startStockAutoRefresh() {
            if (autoRefreshState.stockTimer) {
                window.clearInterval(autoRefreshState.stockTimer);
            }
            autoRefreshState.stockTimer = window.setInterval(() => {
                if (!autoRefreshState.stockLoading) {
                    if (stockDirectoryState.keyword) {
                        loadStockDirectory(stockDirectoryState.page, { silent: true });
                    }
                    if (getCurrentUserId()) {
                        loadFavoriteSnapshot();
                    }
                }
            }, getRefreshIntervalMs(stockRefreshInterval));
        }

        function startRankingAutoRefresh() {
            if (autoRefreshState.rankingTimer) {
                window.clearInterval(autoRefreshState.rankingTimer);
            }
            autoRefreshState.rankingTimer = window.setInterval(() => {
                loadStockRankings();
            }, STOCK_RANKING_REFRESH_MS);
        }

        function applyStockPanelMode(mode, options = {}) {
            const { activatePanel = true } = options;
            const nextMode = mode === 'report' ? 'report' : 'market';
            const targetPanelId = nextMode === 'report' ? 'stockReportPanel' : 'stockMarketPanel';
            if (activatePanel) {
                panels.forEach(panel => {
                    panel.classList.toggle('active', panel.id === targetPanelId);
                });
            }
            if (stockMenuToggle) {
                stockMenuToggle.setAttribute('aria-expanded', 'true');
            }
            stockSubmenu?.classList.add('open');
            stockSubmenuItems.forEach(item => {
                item.classList.toggle('active', item.dataset.stockMode === nextMode);
            });
            if (activatePanel) {
                menuItems.forEach(item => {
                    item.classList.toggle('active', item.id === 'stockMenuToggle');
                });
            }
        }

        function switchPanel(panelId) {
            let normalizedPanelId = panelId === 'stockPanel' ? 'stockMarketPanel' : panelId;
            if (normalizedPanelId === 'userManagePanel' && (!currentUser || !currentUser.is_admin)) {
                normalizedPanelId = 'marketPanel';
            }
            menuItems.forEach(item => {
                const isStockParent = item.id === 'stockMenuToggle' && ['stockMarketPanel', 'stockReportPanel'].includes(normalizedPanelId);
                item.classList.toggle('active', item.dataset.panel === normalizedPanelId || isStockParent);
            });

            panels.forEach(panel => {
                panel.classList.toggle('active', panel.id === normalizedPanelId);
            });

            if (normalizedPanelId === 'sectorPanel' && !sectorState.loaded) {
                loadSectorOptions();
            }
            if ((['stockMarketPanel', 'stockReportPanel'].includes(normalizedPanelId) || normalizedPanelId === 'sentimentPanel' || normalizedPanelId === 'settingsPanel') && !settingsState.stocksLoaded) {
                loadManagedStocks();
            }
            if (normalizedPanelId === 'settingsPanel') {
                if (!settingsState.loaded) {
                    loadProfileSettings();
                    loadReportEmailSettings();
                    loadLlmPromptSettings();
                    loadReportScheduleSettings();
                    settingsState.loaded = true;
                }
                loadManagedStocks();
            }
            if (normalizedPanelId === 'userManagePanel') {
                loadAdminUsers();
            }
            if (normalizedPanelId === 'historyReportPanel') {
                loadHistoryReports();
            }
            if (normalizedPanelId === 'forumPanel') {
                loadForumPosts();
            }
            if (normalizedPanelId === 'sentimentPanel' && !sentimentState.sectorOptionsLoaded) {
                loadSentimentSectorOptions();
            }
            if (normalizedPanelId === 'sentimentPanel' && sentimentState.mode === 'market' && sentimentState.currentItems.length === 0) {
                loadMarketSentiment();
            }
            if (!['stockMarketPanel', 'stockReportPanel'].includes(normalizedPanelId)) {
                stockSubmenu?.classList.remove('open');
                stockMenuToggle?.setAttribute('aria-expanded', 'false');
                stockSubmenuItems.forEach(item => item.classList.remove('active'));
            }
        }

        function showSettingsStockAlert(message, isSuccess = true) {
            settingsStockAlert.textContent = message;
            settingsStockAlert.className = isSuccess ? 'alert alert-success' : 'alert alert-error';
            settingsStockAlert.style.display = 'block';
            setTimeout(() => {
                settingsStockAlert.style.display = 'none';
            }, 3000);
        }

        function showUpdateResult(html, isSuccess = true) {
            if (!updateResult || !updateResultContent) {
                return;
            }
            updateResultContent.innerHTML = html;
            updateResult.style.display = 'block';
            updateResult.style.borderColor = isSuccess ? '#16a34a' : '#dc2626';
        }

        function showPredictResult(html, isSuccess = true) {
            predictResultContent.innerHTML = html;
            predictResult.style.display = 'block';
            predictResult.style.borderColor = isSuccess ? '#f59e0b' : '#dc2626';
        }

        function showMarketPredictResult(html, isSuccess = true) {
            if (!marketPredictResultContent) {
                return;
            }
            const marketPredictResult = document.getElementById('marketPredictResult');
            marketPredictResultContent.innerHTML = html;
            if (marketPredictResult) {
                marketPredictResult.style.display = 'block';
                marketPredictResult.style.borderColor = isSuccess ? '#f59e0b' : '#dc2626';
            }
        }

        function showReportResult(html, isSuccess = true) {
            reportResultContent.innerHTML = html;
            reportResult.style.display = 'block';
            reportResult.style.borderColor = isSuccess ? '#2563eb' : '#dc2626';
        }

        function setProfileStatus(message, type = 'default') {
            if (!profileStatus) {
                return;
            }
            profileStatus.textContent = message;
            profileStatus.className = 'settings-status';
            if (type === 'success') {
                profileStatus.classList.add('success');
            }
            if (type === 'error') {
                profileStatus.classList.add('error');
            }
        }

        function setEmailStatus(message, type = 'default') {
            reportEmailStatus.textContent = message;
            reportEmailStatus.className = 'settings-status';
            if (type === 'success') {
                reportEmailStatus.classList.add('success');
            }
            if (type === 'error') {
                reportEmailStatus.classList.add('error');
            }
        }

        function setLlmPromptStatus(message, type = 'default') {
            llmPromptStatus.textContent = message;
            llmPromptStatus.className = 'settings-status';
            if (type === 'success') {
                llmPromptStatus.classList.add('success');
            }
            if (type === 'error') {
                llmPromptStatus.classList.add('error');
            }
        }

        function setReportScheduleStatus(message, type = 'default') {
            if (!reportScheduleStatus) {
                return;
            }
            reportScheduleStatus.textContent = message;
            reportScheduleStatus.className = 'settings-status';
            if (type === 'success') {
                reportScheduleStatus.classList.add('success');
            }
            if (type === 'error') {
                reportScheduleStatus.classList.add('error');
            }
        }

        function getSelectedScheduleStockCodes() {
            if (!reportScheduleStockList) {
                return [];
            }
            return Array.from(reportScheduleStockList.querySelectorAll('input[type="checkbox"]:checked'))
                .map(input => input.value)
                .filter(Boolean);
        }

        function renderReportScheduleStockOptions(stocks) {
            if (!reportScheduleStockList) {
                return;
            }
            const selectedCodes = new Set(settingsState.reportScheduleSelectedCodes || []);
            if (!stocks || stocks.length === 0) {
                reportScheduleStockList.innerHTML = '<p class="tip">请先在上方“管理我的自选股”中添加股票。</p>';
                return;
            }
            reportScheduleStockList.innerHTML = stocks.map(stock => `
                <label class="schedule-stock-option">
                    <input type="checkbox" value="${stock.stock_code}" ${selectedCodes.has(stock.stock_code) ? 'checked' : ''}>
                    <span>
                        <span class="schedule-stock-option-code">${stock.stock_code}</span>
                        <span class="schedule-stock-option-name"> ${stock.stock_name || ''}</span>
                    </span>
                </label>
            `).join('');
        }

        function setForumStatus(message, type = 'default') {
            if (!forumStatus) {
                return;
            }
            forumStatus.textContent = message;
            forumStatus.className = 'settings-status';
            if (type === 'success') {
                forumStatus.classList.add('success');
            }
            if (type === 'error') {
                forumStatus.classList.add('error');
            }
        }

        function switchForumPanel(mode) {
            const nextMode = mode === 'feed' ? 'feed' : 'compose';
            forumTabs.forEach(tab => {
                tab.classList.toggle('active', tab.dataset.forumPanel === nextMode);
            });
            if (forumComposePanel) {
                forumComposePanel.classList.toggle('active', nextMode === 'compose');
            }
            if (forumFeedPanel) {
                forumFeedPanel.classList.toggle('active', nextMode === 'feed');
            }
            if (nextMode === 'feed') {
                loadForumPosts();
            }
        }

        function updateForumImagePreview() {
            if (!forumImageInput || !forumImagePreview || !forumImagePreviewImg) {
                return;
            }
            const file = forumImageInput.files && forumImageInput.files[0];
            if (!file) {
                forumImagePreview.style.display = 'none';
                forumImagePreviewImg.removeAttribute('src');
                return;
            }
            const reader = new FileReader();
            reader.onload = function(event) {
                forumImagePreviewImg.src = event.target?.result || '';
                forumImagePreview.style.display = 'block';
            };
            reader.readAsDataURL(file);
        }

        function updateProfileAvatarPreview() {
            if (!profileAvatarInput || !profileAvatarPreview) {
                return;
            }
            const file = profileAvatarInput.files && profileAvatarInput.files[0];
            if (!file) {
                renderUserAvatar(profileAvatarPreview, currentUser);
                return;
            }
            const reader = new FileReader();
            reader.onload = function(event) {
                profileAvatarPreview.innerHTML = `<img src="${escapeHtmlAttribute(event.target?.result || '')}" alt="头像预览">`;
            };
            reader.readAsDataURL(file);
        }

        function buildForumAvatarHtml(user) {
            const username = user?.username || '匿名用户';
            if (user?.avatar_url) {
                return `<span class="forum-user-badge forum-user-avatar"><img src="${escapeHtmlAttribute(user.avatar_url)}" alt="${escapeHtmlAttribute(username)}"></span>`;
            }
            return `<span class="forum-user-badge">${escapeHtml(username.slice(0, 1).toUpperCase())}</span>`;
        }

        function renderForumComments(post) {
            const comments = Array.isArray(post?.comments) ? post.comments : [];
            const commentItems = comments.length ? comments.map(comment => `
                <div class="forum-comment-item">
                    <div class="forum-comment-head">
                        <span class="forum-comment-user">${buildForumAvatarHtml(comment)} ${escapeHtml(comment.username || '匿名用户')} · UUID ${escapeHtml(String(comment.uuid || '--'))}</span>
                        <span class="forum-comment-time">${escapeHtml(comment.created_at || '--')}</span>
                    </div>
                    <div class="forum-comment-content">${escapeHtml(comment.content || '')}</div>
                </div>
            `).join('') : '<div class="forum-empty">还没有评论，欢迎来补充观点。</div>';
            const commentTip = currentUser ? `当前评论用户：${currentUser.username}` : '登录后可参与评论';
            return `
                <div class="forum-comments">
                    <div class="forum-comments-head">
                        <span>评论区 · ${comments.length} 条</span>
                        <span>${escapeHtml(commentTip)}</span>
                    </div>
                    <div class="forum-comment-list">${commentItems}</div>
                    <div class="forum-comment-form">
                        <textarea class="settings-textarea forum-comment-input" data-post-id="${escapeHtmlAttribute(post.id)}" placeholder="写下你的看法、补充信息或问题..."></textarea>
                        <div class="forum-comment-actions">
                            <span class="forum-comment-tip">评论会自动记录用户名和时间戳。</span>
                            <button type="button" class="secondary-btn forum-comment-submit-btn" data-post-id="${escapeHtmlAttribute(post.id)}">发表评论</button>
                        </div>
                    </div>
                </div>
            `;
        }

        function renderForumPosts(items) {
            if (!forumList) {
                return;
            }
            const posts = Array.isArray(items) ? items : [];
            forumState.items = posts.slice();
            forumList.innerHTML = posts.length ? posts.map(item => `
                <article class="forum-item">
                    <div class="forum-item-head">
                        <div class="forum-user">
                            ${buildForumAvatarHtml(item)}
                            <span>${escapeHtml(item.username || '匿名用户')} · UUID ${escapeHtml(String(item.uuid || '--'))}</span>
                        </div>
                        <div class="forum-time">${escapeHtml(item.created_at || '--')}</div>
                    </div>
                    <div class="forum-content">${escapeHtml(item.content || '')}</div>
                    ${item.image_url ? `<div class="forum-image"><img src="${escapeHtmlAttribute(item.image_url)}" alt="${escapeHtmlAttribute(item.image_name || '帖子图片')}"></div>` : ''}
                    <div class="forum-item-meta">
                        <div class="forum-item-stats">
                            <span>点赞 ${Number(item.like_count || 0)}</span>
                            <span>评论 ${Number(item.comment_count || (Array.isArray(item.comments) ? item.comments.length : 0))}</span>
                            <span>发布于 ${escapeHtml(item.created_at || '--')}</span>
                        </div>
                        <button type="button" class="secondary-btn forum-like-btn ${item.liked_by_current_user ? 'active' : ''}" data-post-id="${escapeHtmlAttribute(item.id)}">
                            ${item.liked_by_current_user ? '取消点赞' : '点赞'}
                        </button>
                    </div>
                    ${renderForumComments(item)}
                </article>
            `).join('') : '<div class="forum-empty">还没有帖子，来发第一条吧。</div>';
        }

        async function loadForumPosts() {
            if (!forumList) {
                return;
            }
            if (!forumState.loaded) {
                setForumStatus('正在加载论坛帖子...');
            }
            try {
                const query = new URLSearchParams({
                    limit: '50',
                    sort_by: forumState.sortBy || 'created_at',
                    _: String(Date.now())
                });
                if (getCurrentUserId()) {
                    query.set('user_id', String(getCurrentUserId()));
                }
                const response = await fetch(`${BASE_API_URL}/forum/posts?${query.toString()}`, {
                    cache: 'no-store'
                });
                const result = await response.json();
                if (result.code !== 200) {
                    throw new Error(result.msg);
                }
                forumState.loaded = true;
                forumState.sortBy = (result.data && result.data.sort_by) || forumState.sortBy || 'created_at';
                if (forumSortSelect) {
                    forumSortSelect.value = forumState.sortBy;
                }
                renderForumPosts(result.data.items || []);
                setForumStatus(`已加载 ${forumState.items.length} 条帖子。`, 'success');
                if (forumMeta) {
                    const sortLabel = forumState.sortBy === 'likes' ? '点赞量优先' : (forumState.sortBy === 'comments' ? '评论数优先' : '发布时间优先');
                    forumMeta.textContent = `共 ${forumState.items.length} 条帖子，当前按${sortLabel}排序。`;
                }
                if (forumComposerMeta) {
                    forumComposerMeta.textContent = currentUser ? `当前登录用户：${currentUser.username}（UUID ${currentUser.uuid}），发帖后会自动记录时间戳。` : '登录后可直接发帖，系统会自动带上用户名和时间戳。';
                }
            } catch (error) {
                setForumStatus(`论坛帖子加载失败：${error.message}`, 'error');
            }
        }

        async function createForumPost() {
            if (!getCurrentUserId()) {
                setForumStatus('请先登录后再发帖。', 'error');
                return;
            }
            const content = (forumPostContent?.value || '').trim();
            const imageFile = forumImageInput?.files && forumImageInput.files[0] ? forumImageInput.files[0] : null;
            if (!content && !imageFile) {
                setForumStatus('请输入帖子内容或上传图片。', 'error');
                return;
            }
            setForumStatus('正在发布帖子...');
            try {
                const formData = new FormData();
                formData.append('user_id', String(getCurrentUserId()));
                formData.append('content', content);
                if (imageFile) {
                    formData.append('image', imageFile);
                }
                const response = await fetch(`${BASE_API_URL}/forum/posts`, {
                    method: 'POST',
                    body: formData
                });
                const result = await response.json();
                if (result.code !== 200) {
                    throw new Error(result.msg);
                }
                if (forumPostContent) {
                    forumPostContent.value = '';
                }
                if (forumImageInput) {
                    forumImageInput.value = '';
                }
                updateForumImagePreview();
                await loadForumPosts();
                switchForumPanel('feed');
                setForumStatus('发帖成功，已刷新列表。', 'success');
            } catch (error) {
                setForumStatus(`发帖失败：${error.message}`, 'error');
            }
        }

        async function toggleForumLike(postId) {
            if (!getCurrentUserId()) {
                setForumStatus('请先登录后再点赞。', 'error');
                return;
            }
            const normalizedPostId = Number(postId || 0);
            if (!normalizedPostId) {
                setForumStatus('帖子不存在，无法点赞。', 'error');
                return;
            }
            try {
                const response = await fetch(`${BASE_API_URL}/forum/posts/${normalizedPostId}/like`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        user_id: getCurrentUserId()
                    })
                });
                const result = await response.json();
                if (result.code !== 200) {
                    throw new Error(result.msg);
                }
                await loadForumPosts();
                setForumStatus(result.data && result.data.liked ? '点赞成功。' : '已取消点赞。', 'success');
            } catch (error) {
                setForumStatus(`点赞失败：${error.message}`, 'error');
            }
        }

        async function createForumComment(postId, content) {
            if (!getCurrentUserId()) {
                setForumStatus('请先登录后再评论。', 'error');
                return false;
            }
            const normalizedPostId = Number(postId || 0);
            const normalizedContent = String(content || '').trim();
            if (!normalizedPostId) {
                setForumStatus('评论失败：帖子不存在。', 'error');
                return false;
            }
            if (!normalizedContent) {
                setForumStatus('请输入评论内容。', 'error');
                return false;
            }
            setForumStatus('正在发布评论...');
            try {
                const response = await fetch(`${BASE_API_URL}/forum/comments`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        user_id: getCurrentUserId(),
                        post_id: normalizedPostId,
                        content: normalizedContent
                    })
                });
                const result = await response.json();
                if (result.code !== 200) {
                    throw new Error(result.msg);
                }
                await loadForumPosts();
                setForumStatus('评论成功，已刷新帖子。', 'success');
                return true;
            } catch (error) {
                setForumStatus(`评论失败：${error.message}`, 'error');
                return false;
            }
        }

        function switchSentimentMode(mode) {
            sentimentState.mode = mode;
            sentimentTabs.forEach(tab => {
                tab.classList.toggle('active', tab.dataset.sentimentPanel === mode);
            });
            sentimentMarketFilters.style.display = mode === 'market' ? 'flex' : 'none';
            sentimentSectorFilters.style.display = mode === 'sector' ? 'flex' : 'none';
            sentimentStockFilters.style.display = mode === 'stock' ? 'flex' : 'none';
            const cached = sentimentState.cache[mode];
            if (cached) {
                sentimentMeta.textContent = cached.metaText;
                renderSentimentItems(cached.items || []);
            } else {
                sentimentList.style.display = 'none';
                sentimentPagination.style.display = 'none';
                setStatus(sentimentStatus, '请选择条件后开始拉取最新舆情。');
            }
        }

        function getMarketTrendClass(value) {
            if (value > 0) return 'market-up';
            if (value < 0) return 'market-down';
            return 'market-flat';
        }

        function formatSignedNumber(value) {
            const number = Number(value || 0);
            return `${number > 0 ? '+' : ''}${number.toFixed(2)}`;
        }

        function formatValue(value, digits = 2) {
            if (value === null || value === undefined || Number.isNaN(Number(value))) {
                return '--';
            }
            return Number(value).toFixed(digits);
        }

        function formatInteger(value) {
            if (value === null || value === undefined || Number.isNaN(Number(value))) {
                return '--';
            }
            return Number(value).toLocaleString('zh-CN');
        }

        function formatYi(value) {
            if (value === null || value === undefined || Number.isNaN(Number(value))) {
                return '--';
            }
            return `${(Number(value) / 100000000).toFixed(2)}亿`;
        }

        function parseStockCodesInput(value) {
            let normalized = String(value || '').trim();
            if (!normalized) {
                return [];
            }
            for (const separator of ['\n', '\t', '，', ',', '、', ';', '；', '|']) {
                normalized = normalized.replaceAll(separator, ' ');
            }
            const parsed = [];
            normalized.split(' ').forEach(item => {
                const code = item.trim();
                if (code && !parsed.includes(code)) {
                    parsed.push(code);
                }
            });
            return parsed;
        }

        function getPrimaryStockCode() {
            const parsedCodes = parseStockCodesInput(stockCodeInput.value);
            return parsedCodes.length > 0 ? parsedCodes[0] : '';
        }

        function setStatus(element, message, isError = false) {
            element.textContent = message;
            element.className = isError ? 'market-error' : 'market-loading';
            element.style.display = 'block';
        }

        function setSectionMeta(element, updatedAt, source, warning) {
            const sourceTextMap = {
                live: '实时接口',
                cache: '本地缓存',
                fallback: '默认兜底',
                sina: '新浪',
                eastmoney: '东方财富',
                ths: '同花顺',
                'sina+eastmoney': '新浪 + 东方财富',
                'sina+eastmoney+ths': '新浪 + 东方财富 + 同花顺'
            };
            const parts = [];
            if (updatedAt) {
                parts.push(`数据时间：${updatedAt}`);
            }
            if (source && sourceTextMap[source]) {
                parts.push(`来源：${sourceTextMap[source]}`);
            }
            if (warning) {
                parts.push(`提示：${warning}`);
            }
            element.textContent = parts.length ? parts.join(' | ') : '当前暂无数据说明';
        }

        function getSentimentSourceClass(source) {
            const text = String(source || '').toLowerCase();
            if (text.includes('东方财富') || text.includes('eastmoney')) {
                return 'sentiment-pill-eastmoney';
            }
            if (text.includes('同花顺') || text.includes('ths')) {
                return 'sentiment-pill-ths';
            }
            if (text.includes('新浪') || text.includes('sina')) {
                return 'sentiment-pill-sina';
            }
            return 'sentiment-pill-default';
        }

        function renderPagination(container, pagination, callback) {
            if (!pagination || pagination.total === 0) {
                container.style.display = 'none';
                container.innerHTML = '';
                return;
            }

            container.innerHTML = `
                <span class="pagination-info">第 ${pagination.page} / ${pagination.total_pages} 页，共 ${pagination.total} 条</span>
                <button data-page="${pagination.page - 1}" ${pagination.page <= 1 ? 'disabled' : ''}>上一页</button>
                <button data-page="${pagination.page + 1}" ${pagination.page >= pagination.total_pages ? 'disabled' : ''}>下一页</button>
            `;
            container.style.display = 'flex';

            container.querySelectorAll('button').forEach(button => {
                button.addEventListener('click', function() {
                    const targetPage = Number(this.dataset.page);
                    if (!this.disabled) {
                        callback(targetPage);
                    }
                });
            });
        }

        function hideChartTooltip() {
            const chartTooltip = chartShell.querySelector('#chartTooltip');
            const hoverGuide = chartShell.querySelector('#hoverGuide');
            const hoverMarker = chartShell.querySelector('#hoverMarker');

            if (chartTooltip) {
                chartTooltip.style.display = 'none';
            }
            if (hoverGuide) {
                hoverGuide.setAttribute('opacity', '0');
            }
            if (hoverMarker) {
                hoverMarker.setAttribute('opacity', '0');
            }
        }

        function setActiveStockDirectoryRow(stockCode) {
            document.querySelectorAll('.stock-directory-row').forEach(row => {
                row.classList.toggle('active', row.dataset.code === stockCode);
            });
        }

        function renderStockCandlestickChart(data) {
            const points = data.price_series || [];
            if (!points.length) {
                stockChartShell.innerHTML = '<div class="chart-empty">当前暂无走势数据。</div>';
                return;
            }

            const width = 900;
            const height = 280;
            const paddingX = 24;
            const paddingY = 24;
            const minValue = Math.min(...points.map(item => Number(item.low ?? item.close)));
            const maxValue = Math.max(...points.map(item => Number(item.high ?? item.close)));
            const range = Math.max(maxValue - minValue, 0.01);
            const mapY = value => height - paddingY - ((Number(value) - minValue) / range) * (height - paddingY * 2);
            const enrichedPoints = points.map((point, index) => {
                const x = paddingX + index * (width - paddingX * 2) / Math.max(points.length - 1, 1);
                const openPrice = Number(point.open ?? point.close);
                const closePrice = Number(point.close);
                const highPrice = Number(point.high ?? Math.max(openPrice, closePrice));
                const lowPrice = Number(point.low ?? Math.min(openPrice, closePrice));
                return { ...point, x, openPrice, closePrice, highPrice, lowPrice, y: mapY(closePrice) };
            });
            const strokeColor = Number(data.change_percent || 0) >= 0 ? '#dc2626' : '#16a34a';
            const linePath = enrichedPoints.map((point, index) => `${index === 0 ? 'M' : 'L'} ${point.x.toFixed(2)} ${point.y.toFixed(2)}`).join(' ');
            const areaPath = `${linePath} L ${enrichedPoints[enrichedPoints.length - 1].x.toFixed(2)} ${(height - paddingY).toFixed(2)} L ${enrichedPoints[0].x.toFixed(2)} ${(height - paddingY).toFixed(2)} Z`;

            stockChartTitle.textContent = `${stockChartState.activeName || data.stock_name || data.stock_code} 走势`;
            stockChartSubtitle.textContent = data.range_days === 1
                ? `当天分时走势，共 ${points.length} 个时间点`
                : `最近 ${points.length} 个交易日连续走势`;
            stockChartLatest.textContent = formatValue(data.latest_close);
            stockChartLatest.className = `chart-latest ${getMarketTrendClass(Number(data.change_percent || 0))}`;
            stockChartChange.textContent = `${formatSignedNumber(data.change_amount)} / ${formatSignedNumber(data.change_percent)}%`;
            stockChartChange.className = `chart-change ${getMarketTrendClass(Number(data.change_percent || 0))}`;
            stockChartStartDate.textContent = points[0].time_label || points[0].date;
            stockChartEndDate.textContent = points[points.length - 1].time_label || points[points.length - 1].date;
            stockChartMinValue.textContent = `最低 ${minValue.toFixed(2)}`;
            stockChartMaxValue.textContent = `最高 ${maxValue.toFixed(2)}`;
            stockChartShell.innerHTML = `
                <svg class="chart-svg" viewBox="0 0 ${width} ${height}" preserveAspectRatio="none" aria-label="${data.stock_code} 走势">
                    <line x1="${paddingX}" y1="${paddingY}" x2="${paddingX}" y2="${height - paddingY}" stroke="#cbd5e1" stroke-dasharray="4 4"></line>
                    <line x1="${paddingX}" y1="${height - paddingY}" x2="${width - paddingX}" y2="${height - paddingY}" stroke="#cbd5e1" stroke-dasharray="4 4"></line>
                    <path d="${areaPath}" fill="url(#stockLineFill)" opacity="0.16"></path>
                    <path d="${linePath}" fill="none" stroke="${strokeColor}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"></path>
                    <defs>
                        <linearGradient id="stockLineFill" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stop-color="${strokeColor}" stop-opacity="0.35"></stop>
                            <stop offset="100%" stop-color="${strokeColor}" stop-opacity="0.02"></stop>
                        </linearGradient>
                    </defs>
                </svg>
                <div class="chart-tooltip" id="stockChartTooltip"></div>
            `;
            const chartSvg = stockChartShell.querySelector('.chart-svg');
            const chartTooltip = stockChartShell.querySelector('#stockChartTooltip');
            chartSvg.addEventListener('mousemove', function(event) {
                const rect = chartSvg.getBoundingClientRect();
                const shellRect = stockChartShell.getBoundingClientRect();
                const cursorX = ((event.clientX - rect.left) / rect.width) * width;
                const nearestPoint = enrichedPoints.reduce((closest, point) => Math.abs(point.x - cursorX) < Math.abs(closest.x - cursorX) ? point : closest, enrichedPoints[0]);
                chartTooltip.innerHTML = `<div class="chart-tooltip-date">${nearestPoint.time_label || nearestPoint.date}</div><div class="chart-tooltip-value">开 ${formatValue(nearestPoint.openPrice)} 高 ${formatValue(nearestPoint.highPrice)} 低 ${formatValue(nearestPoint.lowPrice)} 收 ${formatValue(nearestPoint.closePrice)}</div>`;
                chartTooltip.style.display = 'block';
                chartTooltip.style.left = `${Math.min(shellRect.width - 150, Math.max(8, event.clientX - shellRect.left + 10))}px`;
                chartTooltip.style.top = `${Math.max(8, event.clientY - shellRect.top - 50)}px`;
            });
            chartSvg.addEventListener('mouseleave', function() {
                chartTooltip.style.display = 'none';
            });
        }

        function renderStockVolumeChart(data) {
            const points = data.volume_series || [];
            if (!points.length) {
                stockChartShell.innerHTML = '<div class="chart-empty">当前暂无成交量数据。</div>';
                return;
            }

            const width = 900;
            const height = 280;
            const paddingX = 24;
            const paddingY = 24;
            const maxVolume = Math.max(...points.map(item => Number(item.volume || 0)), 1);
            const barGap = (width - paddingX * 2) / Math.max(points.length, 1);
            const barWidth = Math.max(6, Math.min(16, barGap * 0.66));
            const enrichedPoints = points.map((point, index) => {
                const volume = Number(point.volume || 0);
                const openPrice = Number(point.open ?? point.close);
                const closePrice = Number(point.close);
                const color = closePrice >= openPrice ? '#dc2626' : '#16a34a';
                const barHeight = Math.max(2, (volume / maxVolume) * (height - paddingY * 2));
                const x = paddingX + barGap * index + (barGap - barWidth) / 2;
                const y = height - paddingY - barHeight;
                return { ...point, x, y, volume, openPrice, closePrice, color, barHeight };
            });
            const bars = enrichedPoints.map(point => {
                return `<rect x="${point.x.toFixed(2)}" y="${point.y.toFixed(2)}" width="${barWidth.toFixed(2)}" height="${point.barHeight.toFixed(2)}" rx="3" fill="${point.color}" opacity="0.9"></rect>`;
            }).join('');

            stockChartTitle.textContent = `${stockChartState.activeName || data.stock_name || data.stock_code} 成交量`;
            stockChartSubtitle.textContent = data.range_days === 1 ? '当天分时成交量' : `最近 ${points.length} 个交易日真实成交量`;
            stockChartLatest.textContent = formatYi(points[points.length - 1].amount);
            stockChartLatest.className = 'chart-latest';
            stockChartChange.textContent = `最新成交量 ${formatInteger(points[points.length - 1].volume)}`;
            stockChartChange.className = 'chart-change';
            stockChartStartDate.textContent = points[0].time_label || points[0].date;
            stockChartEndDate.textContent = points[points.length - 1].time_label || points[points.length - 1].date;
            stockChartMinValue.textContent = '最低 0';
            stockChartMaxValue.textContent = `最高 ${formatInteger(maxVolume)}`;
            stockChartShell.innerHTML = `
                <svg class="chart-svg" viewBox="0 0 ${width} ${height}" preserveAspectRatio="none" aria-label="${data.stock_code} 成交量">
                    <line x1="${paddingX}" y1="${height - paddingY}" x2="${width - paddingX}" y2="${height - paddingY}" stroke="#cbd5e1" stroke-dasharray="4 4"></line>
                    ${bars}
                </svg>
                <div class="chart-tooltip" id="stockChartTooltip"></div>
            `;
            const chartSvg = stockChartShell.querySelector('.chart-svg');
            const chartTooltip = stockChartShell.querySelector('#stockChartTooltip');
            chartSvg.addEventListener('mousemove', function(event) {
                const rect = chartSvg.getBoundingClientRect();
                const shellRect = stockChartShell.getBoundingClientRect();
                const cursorX = ((event.clientX - rect.left) / rect.width) * width;
                const nearestPoint = enrichedPoints.reduce((closest, point) => Math.abs((point.x + barWidth / 2) - cursorX) < Math.abs((closest.x + barWidth / 2) - cursorX) ? point : closest, enrichedPoints[0]);
                chartTooltip.innerHTML = `<div class="chart-tooltip-date">${nearestPoint.time_label || nearestPoint.date}</div><div class="chart-tooltip-value">成交量 ${formatInteger(nearestPoint.volume)} / 成交额 ${formatYi(nearestPoint.amount)}</div>`;
                chartTooltip.style.display = 'block';
                chartTooltip.style.left = `${Math.min(shellRect.width - 150, Math.max(8, event.clientX - shellRect.left + 10))}px`;
                chartTooltip.style.top = `${Math.max(8, event.clientY - shellRect.top - 50)}px`;
            });
            chartSvg.addEventListener('mouseleave', function() {
                chartTooltip.style.display = 'none';
            });
        }

        function renderStockCompareChart(data) {
            const compare = data.market_compare || {};
            const stockSeries = compare.stock_series || [];
            const marketSeries = compare.market_series || [];
            if (!stockSeries.length || !marketSeries.length) {
                stockChartShell.innerHTML = '<div class="chart-empty">当前暂无相对大盘对比数据。</div>';
                return;
            }

            const width = 900;
            const height = 280;
            const paddingX = 24;
            const paddingY = 24;
            const stockValues = stockSeries.map(item => Number(item.close));
            const marketValues = marketSeries.map(item => Number(item.close));
            const stockBase = stockValues[0];
            const marketBase = marketValues[0];
            const stockNorm = stockValues.map(value => value / stockBase * 100);
            const marketNorm = marketValues.map(value => value / marketBase * 100);
            const allValues = stockNorm.concat(marketNorm);
            const minValue = Math.min(...allValues);
            const maxValue = Math.max(...allValues);
            const range = Math.max(maxValue - minValue, 0.01);
            const mapY = value => height - paddingY - ((value - minValue) / range) * (height - paddingY * 2);
            const buildPath = values => values.map((value, index) => {
                const x = paddingX + index * (width - paddingX * 2) / Math.max(values.length - 1, 1);
                return `${index === 0 ? 'M' : 'L'} ${x.toFixed(2)} ${mapY(value).toFixed(2)}`;
            }).join(' ');

            stockChartTitle.textContent = `${stockChartState.activeName || data.stock_name || data.stock_code} 相对大盘`;
            stockChartSubtitle.textContent = `与${compare.market_name || '上证指数'}近 ${data.range_days} 天归一化走势对比`;
            stockChartLatest.textContent = `${formatValue(compare.excess_return)}%`;
            stockChartLatest.className = `chart-latest ${getMarketTrendClass(Number(compare.excess_return || 0))}`;
            stockChartChange.textContent = `个股 ${formatValue(compare.stock_return)}% / 大盘 ${formatValue(compare.market_return)}%`;
            stockChartChange.className = 'chart-change';
            stockChartStartDate.textContent = stockSeries[0].date;
            stockChartEndDate.textContent = stockSeries[stockSeries.length - 1].date;
            stockChartMinValue.textContent = `最低 ${minValue.toFixed(2)}`;
            stockChartMaxValue.textContent = `最高 ${maxValue.toFixed(2)}`;
            stockChartShell.innerHTML = `
                <svg class="chart-svg" viewBox="0 0 ${width} ${height}" preserveAspectRatio="none" aria-label="${data.stock_code} 相对大盘对比">
                    <line x1="${paddingX}" y1="${paddingY}" x2="${paddingX}" y2="${height - paddingY}" stroke="#cbd5e1" stroke-dasharray="4 4"></line>
                    <line x1="${paddingX}" y1="${height - paddingY}" x2="${width - paddingX}" y2="${height - paddingY}" stroke="#cbd5e1" stroke-dasharray="4 4"></line>
                    <path d="${buildPath(marketNorm)}" fill="none" stroke="#94a3b8" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"></path>
                    <path d="${buildPath(stockNorm)}" fill="none" stroke="#2563eb" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"></path>
                </svg>
            `;
        }

        function renderStockChart() {
            if (!stockChartState.data) {
                stockChartCard.style.display = 'none';
                return;
            }
            if (stockChartState.activeType === 'volume') {
                renderStockVolumeChart(stockChartState.data);
            } else if (stockChartState.activeType === 'compare') {
                renderStockCompareChart(stockChartState.data);
            } else {
                renderStockCandlestickChart(stockChartState.data);
            }
            stockChartCard.style.display = 'block';
            setStockChartType(stockChartState.activeType);
            setActiveStockDirectoryRow(stockChartState.activeCode);
        }

        async function loadStockCharts(stockCode, stockName = '', options = {}) {
            const { silent = false } = options;
            if (!stockCode) {
                stockChartCard.style.display = 'none';
                return;
            }
            stockChartState.activeCode = stockCode;
            stockChartState.activeName = stockName || stockCode;
            if (!silent) {
                stockChartCard.style.display = 'block';
                stockChartTitle.textContent = `${stockName || stockCode} 图表加载中`;
                stockChartSubtitle.textContent = '正在获取真实历史数据...';
                stockChartShell.innerHTML = '<div class="chart-empty">正在获取图表数据...</div>';
            }
            try {
                const response = await fetch(`${BASE_API_URL}/stock_charts?stock_code=${encodeURIComponent(stockCode)}&stock_name=${encodeURIComponent(stockName)}&days=${stockChartState.rangeDays}`);
                const result = await response.json();
                if (result.code !== 200) {
                    throw new Error(result.msg);
                }
                stockChartState.data = result.data;
                renderStockChart();
            } catch (error) {
                stockChartShell.innerHTML = `<div class="chart-empty">图表加载失败：${error.message}</div>`;
                stockChartCard.style.display = 'block';
            }
        }

        function renderMarketCards() {
            if (!marketState.data || !marketState.data.indices || marketState.data.indices.length === 0) {
                indexCards.style.display = 'none';
                marketChartCard.style.display = 'none';
                return;
            }

            indexCards.innerHTML = marketState.data.indices.map(item => `
                <div class="index-card ${item.key === marketState.activeKey ? 'active' : ''}" data-key="${item.key}">
                    <div class="index-card-title">${item.name}</div>
                    <div class="index-card-value ${getMarketTrendClass(item.change_percent)}">${item.latest_close.toFixed(2)}</div>
                    <div class="${getMarketTrendClass(item.change_percent)}">
                        ${formatSignedNumber(item.change_amount)} / ${formatSignedNumber(item.change_percent)}%
                    </div>
                </div>
            `).join('');

            indexCards.style.display = 'grid';

            document.querySelectorAll('.index-card').forEach(card => {
                card.addEventListener('click', function() {
                    marketState.activeKey = this.dataset.key;
                    renderMarketCards();
                    renderMarketChart();
                });
            });
        }

        function calculateSma(values, period) {
            return values.map((_, index) => {
                if (index + 1 < period) {
                    return null;
                }
                const window = values.slice(index - period + 1, index + 1);
                const valid = window.filter(value => Number.isFinite(value));
                if (valid.length !== period) {
                    return null;
                }
                return valid.reduce((sum, value) => sum + value, 0) / period;
            });
        }

        function calculateEma(values, period) {
            const multiplier = 2 / (period + 1);
            let ema = null;
            return values.map((value, index) => {
                if (!Number.isFinite(value)) {
                    return null;
                }
                if (index === 0 || ema === null) {
                    ema = value;
                } else {
                    ema = (value - ema) * multiplier + ema;
                }
                return ema;
            });
        }

        function calculateRsi(values, period = 14) {
            const result = new Array(values.length).fill(null);
            if (values.length <= period) {
                return result;
            }
            let gains = 0;
            let losses = 0;
            for (let index = 1; index <= period; index += 1) {
                const delta = values[index] - values[index - 1];
                gains += Math.max(delta, 0);
                losses += Math.max(-delta, 0);
            }
            let avgGain = gains / period;
            let avgLoss = losses / period;
            result[period] = avgLoss === 0 ? 100 : 100 - (100 / (1 + avgGain / avgLoss));
            for (let index = period + 1; index < values.length; index += 1) {
                const delta = values[index] - values[index - 1];
                avgGain = ((avgGain * (period - 1)) + Math.max(delta, 0)) / period;
                avgLoss = ((avgLoss * (period - 1)) + Math.max(-delta, 0)) / period;
                result[index] = avgLoss === 0 ? 100 : 100 - (100 / (1 + avgGain / avgLoss));
            }
            return result;
        }

        function buildMarketIndicators(points) {
            const closes = points.map(point => Number(point.close || 0));
            const ma5 = calculateSma(closes, 5);
            const ma10 = calculateSma(closes, 10);
            const ma20 = calculateSma(closes, 20);
            const rsi14 = calculateRsi(closes, 14);
            const ema12 = calculateEma(closes, 12);
            const ema26 = calculateEma(closes, 26);
            const dif = closes.map((_, index) => {
                if (!Number.isFinite(ema12[index]) || !Number.isFinite(ema26[index])) {
                    return null;
                }
                return ema12[index] - ema26[index];
            });
            const dea = calculateEma(dif.map(value => Number.isFinite(value) ? value : 0), 9).map((value, index) => (
                Number.isFinite(dif[index]) ? value : null
            ));
            const histogram = dif.map((value, index) => (
                Number.isFinite(value) && Number.isFinite(dea[index]) ? (value - dea[index]) * 2 : null
            ));
            return { ma5, ma10, ma20, rsi14, dif, dea, histogram };
        }

        function renderRsiChart(shell, points, rsiSeries, indexName) {
            const entries = points.map((point, index) => ({
                label: point.time_label || point.date,
                value: rsiSeries[index],
            })).filter(item => Number.isFinite(item.value));
            if (!entries.length) {
                shell.innerHTML = '<div class="chart-empty">RSI 数据不足。</div>';
                return;
            }
            const width = 900;
            const height = 220;
            const paddingX = 24;
            const paddingY = 22;
            const mapX = index => paddingX + (index * (width - paddingX * 2)) / Math.max(entries.length - 1, 1);
            const mapY = value => height - paddingY - ((value - 0) / 100) * (height - paddingY * 2);
            const linePath = entries.map((item, index) => `${index === 0 ? 'M' : 'L'} ${mapX(index).toFixed(2)} ${mapY(item.value).toFixed(2)}`).join(' ');
            shell.innerHTML = `
                <svg class="chart-svg" viewBox="0 0 ${width} ${height}" preserveAspectRatio="none" aria-label="${indexName} RSI 图">
                    <line x1="${paddingX}" y1="${mapY(70).toFixed(2)}" x2="${width - paddingX}" y2="${mapY(70).toFixed(2)}" stroke="#ef4444" stroke-dasharray="6 6" opacity="0.55"></line>
                    <line x1="${paddingX}" y1="${mapY(30).toFixed(2)}" x2="${width - paddingX}" y2="${mapY(30).toFixed(2)}" stroke="#3b82f6" stroke-dasharray="6 6" opacity="0.55"></line>
                    <path d="${linePath}" fill="none" stroke="#f59e0b" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"></path>
                </svg>
            `;
        }

        function renderMacdChart(shell, points, indicators, indexName) {
            const entries = points.map((point, index) => ({
                label: point.time_label || point.date,
                dif: indicators.dif[index],
                dea: indicators.dea[index],
                histogram: indicators.histogram[index],
            })).filter(item => Number.isFinite(item.histogram) || Number.isFinite(item.dif) || Number.isFinite(item.dea));
            if (!entries.length) {
                shell.innerHTML = '<div class="chart-empty">MACD 数据不足。</div>';
                return;
            }
            const width = 900;
            const height = 220;
            const paddingX = 24;
            const paddingY = 22;
            const values = entries.flatMap(item => [item.dif, item.dea, item.histogram]).filter(Number.isFinite);
            const minValue = Math.min(...values, 0);
            const maxValue = Math.max(...values, 0);
            const range = maxValue - minValue || 1;
            const mapX = index => paddingX + (index * (width - paddingX * 2)) / Math.max(entries.length - 1, 1);
            const mapY = value => height - paddingY - ((value - minValue) / range) * (height - paddingY * 2);
            const zeroY = mapY(0);
            const difPath = entries.map((item, index) => Number.isFinite(item.dif) ? `${index === 0 ? 'M' : 'L'} ${mapX(index).toFixed(2)} ${mapY(item.dif).toFixed(2)}` : '').join(' ');
            const deaPath = entries.map((item, index) => Number.isFinite(item.dea) ? `${index === 0 ? 'M' : 'L'} ${mapX(index).toFixed(2)} ${mapY(item.dea).toFixed(2)}` : '').join(' ');
            const barGap = (width - paddingX * 2) / Math.max(entries.length, 1);
            const barWidth = Math.max(4, Math.min(12, barGap * 0.6));
            const bars = entries.map((item, index) => {
                const value = Number(item.histogram || 0);
                const x = mapX(index) - barWidth / 2;
                const y = value >= 0 ? mapY(value) : zeroY;
                const barHeight = Math.max(2, Math.abs(mapY(value) - zeroY));
                const color = value >= 0 ? '#dc2626' : '#16a34a';
                return `<rect x="${x.toFixed(2)}" y="${y.toFixed(2)}" width="${barWidth.toFixed(2)}" height="${barHeight.toFixed(2)}" rx="2" fill="${color}" opacity="0.75"></rect>`;
            }).join('');
            shell.innerHTML = `
                <svg class="chart-svg" viewBox="0 0 ${width} ${height}" preserveAspectRatio="none" aria-label="${indexName} MACD 图">
                    <line x1="${paddingX}" y1="${zeroY.toFixed(2)}" x2="${width - paddingX}" y2="${zeroY.toFixed(2)}" stroke="#cbd5e1" stroke-dasharray="4 4"></line>
                    ${bars}
                    <path d="${difPath}" fill="none" stroke="#2563eb" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"></path>
                    <path d="${deaPath}" fill="none" stroke="#f59e0b" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"></path>
                </svg>
            `;
        }

        function renderMarketBars(shell, points, field, label) {
            if (!points.length) {
                shell.innerHTML = '<div class="chart-empty">暂无数据。</div>';
                return;
            }
            const displayPoints = points.length > 90
                ? points.filter((_, index) => index % Math.ceil(points.length / 90) === 0)
                : points;
            const width = 900;
            const height = 220;
            const paddingX = 24;
            const paddingY = 18;
            const values = displayPoints.map(item => Number(item[field] || 0));
            const maxValue = Math.max(...values, 1);
            const barGap = (width - paddingX * 2) / Math.max(displayPoints.length, 1);
            const barWidth = Math.max(8, Math.min(18, barGap * 0.68));
            const enrichedPoints = displayPoints.map((point, index) => {
                const value = Number(point[field] || 0);
                const x = paddingX + barGap * index + (barGap - barWidth) / 2;
                const barHeight = Math.max(2, (value / maxValue) * (height - paddingY * 2));
                const y = height - paddingY - barHeight;
                const color = Number(point.close || 0) >= Number(point.open || point.close || 0) ? '#dc2626' : '#16a34a';
                return { ...point, x, y, barHeight, color, value };
            });
            const bars = enrichedPoints.map(point => {
                return `<rect x="${point.x.toFixed(2)}" y="${point.y.toFixed(2)}" width="${barWidth.toFixed(2)}" height="${point.barHeight.toFixed(2)}" rx="3" fill="${point.color}" opacity="0.88"></rect>`;
            }).join('');
            shell.innerHTML = `
                <svg class="chart-svg" viewBox="0 0 ${width} ${height}" preserveAspectRatio="none" aria-label="${label}">
                    <line x1="${paddingX}" y1="${height - paddingY}" x2="${width - paddingX}" y2="${height - paddingY}" stroke="#cbd5e1" stroke-dasharray="4 4"></line>
                    ${bars}
                </svg>
                <div class="chart-tooltip" id="marketBarTooltip"></div>
            `;
            const chartSvg = shell.querySelector('.chart-svg');
            const chartTooltip = shell.querySelector('#marketBarTooltip');
            chartSvg.addEventListener('mousemove', function(event) {
                const rect = chartSvg.getBoundingClientRect();
                const shellRect = shell.getBoundingClientRect();
                const cursorX = ((event.clientX - rect.left) / rect.width) * width;
                const nearestPoint = enrichedPoints.reduce((closest, point) => {
                    return Math.abs((point.x + barWidth / 2) - cursorX) < Math.abs((closest.x + barWidth / 2) - cursorX) ? point : closest;
                }, enrichedPoints[0]);
                chartTooltip.innerHTML = `<div class="chart-tooltip-date">${nearestPoint.time_label || nearestPoint.date}</div><div class="chart-tooltip-value">${label}：${field === 'amount' ? formatYi(nearestPoint.value) : formatInteger(nearestPoint.value)}</div>`;
                chartTooltip.style.display = 'block';
                chartTooltip.style.left = `${Math.min(shellRect.width - 150, Math.max(8, event.clientX - shellRect.left + 10))}px`;
                chartTooltip.style.top = `${Math.max(8, event.clientY - shellRect.top - 50)}px`;
            });
            chartSvg.addEventListener('mouseleave', function() {
                chartTooltip.style.display = 'none';
            });
        }

        function fitAr1(diffValues) {
            if (!Array.isArray(diffValues) || diffValues.length < 3) {
                return { intercept: 0, phi: 0 };
            }
            const xValues = diffValues.slice(0, -1);
            const yValues = diffValues.slice(1);
            const xMean = xValues.reduce((sum, value) => sum + value, 0) / xValues.length;
            const yMean = yValues.reduce((sum, value) => sum + value, 0) / yValues.length;
            let numerator = 0;
            let denominator = 0;
            xValues.forEach((value, index) => {
                numerator += (value - xMean) * (yValues[index] - yMean);
                denominator += (value - xMean) ** 2;
            });
            const phi = denominator ? numerator / denominator : 0;
            return { intercept: yMean - phi * xMean, phi };
        }

        function forecastArima110(closeValues, steps) {
            if (!Array.isArray(closeValues) || closeValues.length < 20 || steps <= 0) {
                return [];
            }
            const diffValues = [];
            for (let index = 1; index < closeValues.length; index += 1) {
                diffValues.push(Number(closeValues[index]) - Number(closeValues[index - 1]));
            }
            const { intercept, phi } = fitAr1(diffValues);
            let previousDiff = diffValues[diffValues.length - 1];
            let predictedClose = Number(closeValues[closeValues.length - 1]);
            const forecasts = [];
            for (let step = 0; step < steps; step += 1) {
                const nextDiff = intercept + phi * previousDiff;
                predictedClose += nextDiff;
                previousDiff = nextDiff;
                forecasts.push(Number(predictedClose.toFixed(2)));
            }
            return forecasts;
        }

        function getNextTradingDateLabel(baseDate, offset) {
            const date = new Date(`${baseDate}T00:00:00`);
            let remaining = Math.max(1, Number(offset || 1));
            while (remaining > 0) {
                date.setDate(date.getDate() + 1);
                const day = date.getDay();
                if (day !== 0 && day !== 6) {
                    remaining -= 1;
                }
            }
            return `${date.getFullYear()}-${padDateTimeNumber(date.getMonth() + 1)}-${padDateTimeNumber(date.getDate())}`;
        }

        function buildIntradayForecastLabels(lastLabel) {
            const text = String(lastLabel || '').trim();
            if (!/^\d{2}:\d{2}$/.test(text)) {
                return [];
            }
            const [hourText] = text.split(':');
            const baseHour = Number(hourText);
            if (!Number.isFinite(baseHour)) {
                return [];
            }
            const labels = [];
            const limitHour = Math.min(15, baseHour + 3);
            for (let hour = baseHour + 1; hour <= limitHour; hour += 1) {
                labels.push(`${padDateTimeNumber(hour)}:00`);
            }
            return labels;
        }

        function buildMarketArimaForecast(indexKey, points, rangeDays) {
            if (indexKey !== 'sh000001' || !Array.isArray(points) || points.length < 20) {
                return [];
            }
            const closeValues = points.map(point => Number(point.close)).filter(Number.isFinite);
            if (closeValues.length < 20) {
                return [];
            }

            let labels = [];
            if (Number(rangeDays) === 1) {
                labels = buildIntradayForecastLabels(points[points.length - 1].time_label || '');
            } else {
                const forecastDaysMap = { 30: 7, 90: 14, 365: 30 };
                const steps = forecastDaysMap[Number(rangeDays)] || 0;
                for (let offset = 1; offset <= steps; offset += 1) {
                    labels.push(getNextTradingDateLabel(points[points.length - 1].date, offset));
                }
            }
            const forecastValues = forecastArima110(closeValues, labels.length);
            return forecastValues.map((value, index) => ({
                date: Number(rangeDays) === 1 ? points[points.length - 1].date : labels[index],
                time_label: labels[index],
                close: value,
                is_forecast: true
            }));
        }

        function renderMarketChart() {
            if (!marketState.data || !marketState.activeKey) {
                marketChartCard.style.display = 'none';
                return;
            }

            const currentIndex = marketState.data.indices.find(item => item.key === marketState.activeKey);
            if (!currentIndex || !currentIndex.series || currentIndex.series.length === 0) {
                marketChartCard.style.display = 'none';
                return;
            }

            const points = currentIndex.series;
            const forecastPoints = buildMarketArimaForecast(currentIndex.key, points, marketState.data.range_days);
            const indicators = buildMarketIndicators(points);
            const combinedPoints = points.concat(forecastPoints);
            const minValue = Math.min(...combinedPoints.map(item => Number(item.low ?? item.close)));
            const maxValue = Math.max(...combinedPoints.map(item => Number(item.high ?? item.close)));
            const range = maxValue - minValue || 1;
            const width = 900;
            const height = 280;
            const paddingX = 24;
            const paddingY = 26;
            const svgPoints = combinedPoints.map((point, index) => {
                const x = paddingX + (index * (width - paddingX * 2)) / Math.max(combinedPoints.length - 1, 1);
                const y = height - paddingY - ((point.close - minValue) / range) * (height - paddingY * 2);
                return { x, y, ...point };
            });
            const actualSvgPoints = svgPoints.slice(0, points.length);
            const forecastSvgPoints = svgPoints.slice(points.length - 1);
            const latestPoint = actualSvgPoints[actualSvgPoints.length - 1];
            const trendClass = getMarketTrendClass(currentIndex.change_percent);
            const strokeColor = currentIndex.change_percent > 0 ? '#dc2626' : currentIndex.change_percent < 0 ? '#16a34a' : '#475569';
            const linePath = actualSvgPoints.map((point, index) => `${index === 0 ? 'M' : 'L'} ${point.x.toFixed(2)} ${point.y.toFixed(2)}`).join(' ');
            const areaPath = `${linePath} L ${actualSvgPoints[actualSvgPoints.length - 1].x.toFixed(2)} ${(height - paddingY).toFixed(2)} L ${actualSvgPoints[0].x.toFixed(2)} ${(height - paddingY).toFixed(2)} Z`;
            const forecastPath = forecastSvgPoints.length > 1 ? forecastSvgPoints.map((point, index) => `${index === 0 ? 'M' : 'L'} ${point.x.toFixed(2)} ${point.y.toFixed(2)}`).join(' ') : '';
            const maConfigs = [
                { key: 'ma5', label: 'MA5', color: '#2563eb', series: indicators.ma5 },
                { key: 'ma10', label: 'MA10', color: '#f59e0b', series: indicators.ma10 },
                { key: 'ma20', label: 'MA20', color: '#7c3aed', series: indicators.ma20 },
            ];
            const maPaths = maConfigs.map(config => {
                const commands = [];
                config.series.forEach((value, index) => {
                    if (!Number.isFinite(value)) {
                        return;
                    }
                    const x = paddingX + (index * (width - paddingX * 2)) / Math.max(points.length - 1, 1);
                    const y = height - paddingY - ((value - minValue) / range) * (height - paddingY * 2);
                    commands.push(`${commands.length === 0 ? 'M' : 'L'} ${x.toFixed(2)} ${y.toFixed(2)}`);
                });
                return { ...config, path: commands.join(' ') };
            });
            const latestRsi = [...indicators.rsi14].reverse().find(Number.isFinite);
            const latestDif = [...indicators.dif].reverse().find(Number.isFinite);
            const latestDea = [...indicators.dea].reverse().find(Number.isFinite);
            const latestMa5 = [...indicators.ma5].reverse().find(Number.isFinite);
            const latestMa20 = [...indicators.ma20].reverse().find(Number.isFinite);

            chartTitle.textContent = currentIndex.name;
            chartSubtitle.textContent = marketState.data.range_days >= 365 ? '最近 1 年指数连续走势' : `最近 ${marketState.data.range_days} 天指数连续走势`;
            if (forecastPoints.length) {
                chartSubtitle.textContent += ` + ARIMA 预测延长线`;
            }
            chartLatest.textContent = currentIndex.latest_close.toFixed(2);
            chartLatest.className = `chart-latest ${trendClass}`;
            chartChange.textContent = `${formatSignedNumber(currentIndex.change_amount)} / ${formatSignedNumber(currentIndex.change_percent)}%`;
            chartChange.className = `chart-change ${trendClass}`;
            chartStartDate.textContent = points[0].time_label || points[0].date;
            chartEndDate.textContent = forecastPoints.length ? `${forecastPoints[forecastPoints.length - 1].time_label || forecastPoints[forecastPoints.length - 1].date}（预测）` : (points[points.length - 1].time_label || points[points.length - 1].date);
            chartMinValue.textContent = `最低 ${minValue.toFixed(2)}`;
            chartMaxValue.textContent = `最高 ${maxValue.toFixed(2)}`;
            if (marketIndicatorStrip) {
                marketIndicatorStrip.innerHTML = `
                    <div class="market-indicator-pill">
                        <div class="market-indicator-label">MA 结构</div>
                        <div class="market-indicator-value">${Number.isFinite(latestMa5) && Number.isFinite(latestMa20) ? (latestMa5 >= latestMa20 ? '短线偏强' : '短线偏弱') : '--'}</div>
                    </div>
                    <div class="market-indicator-pill">
                        <div class="market-indicator-label">RSI14</div>
                        <div class="market-indicator-value">${Number.isFinite(latestRsi) ? latestRsi.toFixed(2) : '--'}</div>
                    </div>
                    <div class="market-indicator-pill">
                        <div class="market-indicator-label">MACD</div>
                        <div class="market-indicator-value">${Number.isFinite(latestDif) && Number.isFinite(latestDea) ? (latestDif >= latestDea ? '动量偏多' : '动量偏空') : '--'}</div>
                    </div>
                `;
            }
            if (marketMaLegend) {
                marketMaLegend.innerHTML = maPaths.map(item => `
                    <span class="market-ma-item">
                        <span class="market-ma-dot" style="background:${item.color};"></span>
                        <span>${item.label}${Number.isFinite(item.series[item.series.length - 1]) ? ` ${item.series[item.series.length - 1].toFixed(2)}` : ''}</span>
                    </span>
                `).join('') + (forecastSvgPoints.length > 1 ? `
                    <span class="market-ma-item">
                        <span class="market-ma-dot" style="background:${strokeColor};"></span>
                        <span>ARIMA 预测延长线</span>
                    </span>
                ` : '');
            }

            chartShell.innerHTML = `
                <svg class="chart-svg" viewBox="0 0 ${width} ${height}" preserveAspectRatio="none" aria-label="${currentIndex.name}走势图">
                    <line x1="${paddingX}" y1="${paddingY}" x2="${paddingX}" y2="${height - paddingY}" stroke="#cbd5e1" stroke-dasharray="4 4"></line>
                    <line x1="${paddingX}" y1="${height - paddingY}" x2="${width - paddingX}" y2="${height - paddingY}" stroke="#cbd5e1" stroke-dasharray="4 4"></line>
                    <line id="hoverGuide" x1="${latestPoint.x.toFixed(2)}" y1="${paddingY}" x2="${latestPoint.x.toFixed(2)}" y2="${height - paddingY}" stroke="${strokeColor}" stroke-width="1.5" stroke-dasharray="4 4" opacity="0"></line>
                    <path d="${areaPath}" fill="url(#marketLineFill)" opacity="0.18"></path>
                    ${maPaths.map(item => item.path ? `<path d="${item.path}" fill="none" stroke="${item.color}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" opacity="0.9"></path>` : '').join('')}
                    <path d="${linePath}" fill="none" stroke="${strokeColor}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"></path>
                    ${forecastPath ? `<path d="${forecastPath}" fill="none" stroke="${strokeColor}" stroke-width="3" stroke-dasharray="10 7" stroke-linecap="round" stroke-linejoin="round" opacity="0.95"></path>` : ''}
                    <defs>
                        <linearGradient id="marketLineFill" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stop-color="${strokeColor}" stop-opacity="0.4"></stop>
                            <stop offset="100%" stop-color="${strokeColor}" stop-opacity="0.02"></stop>
                        </linearGradient>
                    </defs>
                    <circle id="hoverMarker" cx="${latestPoint.x.toFixed(2)}" cy="${latestPoint.y.toFixed(2)}" r="6.5" fill="#ffffff" stroke="${strokeColor}" stroke-width="3" opacity="0"></circle>
                </svg>
                <div class="chart-tooltip" id="chartTooltip"></div>
            `;

            const chartSvg = chartShell.querySelector('.chart-svg');
            const chartTooltip = chartShell.querySelector('#chartTooltip');
            const hoverGuide = chartShell.querySelector('#hoverGuide');
            const hoverMarker = chartShell.querySelector('#hoverMarker');

            chartSvg.addEventListener('mousemove', function(event) {
                const rect = chartSvg.getBoundingClientRect();
                const shellRect = chartShell.getBoundingClientRect();
                const cursorX = ((event.clientX - rect.left) / rect.width) * width;
                const nearestPoint = svgPoints.reduce((closest, point) => {
                    return Math.abs(point.x - cursorX) < Math.abs(closest.x - cursorX) ? point : closest;
                }, svgPoints[0]);

                hoverGuide.setAttribute('x1', nearestPoint.x.toFixed(2));
                hoverGuide.setAttribute('x2', nearestPoint.x.toFixed(2));
                hoverGuide.setAttribute('opacity', '1');
                hoverMarker.setAttribute('cx', nearestPoint.x.toFixed(2));
                hoverMarker.setAttribute('cy', nearestPoint.y.toFixed(2));
                hoverMarker.setAttribute('opacity', '1');

                chartTooltip.innerHTML = `
                    <div class="chart-tooltip-date">${nearestPoint.time_label || nearestPoint.date}</div>
                    <div class="chart-tooltip-value">${nearestPoint.is_forecast ? 'ARIMA预测' : '指数现值'} ${formatValue(nearestPoint.close)}</div>
                `;
                chartTooltip.style.display = 'block';

                const pointClientX = rect.left + (nearestPoint.x / width) * rect.width;
                const pointClientY = rect.top + (nearestPoint.y / height) * rect.height;
                const tooltipWidth = chartTooltip.offsetWidth || 132;
                const tooltipHeight = chartTooltip.offsetHeight || 52;

                let tooltipLeft = pointClientX - shellRect.left + 14;
                let tooltipTop = pointClientY - shellRect.top - tooltipHeight - 12;

                if (tooltipLeft + tooltipWidth > shellRect.width - 8) {
                    tooltipLeft = pointClientX - shellRect.left - tooltipWidth - 14;
                }
                if (tooltipLeft < 8) {
                    tooltipLeft = 8;
                }
                if (tooltipTop < 8) {
                    tooltipTop = pointClientY - shellRect.top + 14;
                }

                chartTooltip.style.left = `${tooltipLeft}px`;
                chartTooltip.style.top = `${tooltipTop}px`;
            });

            chartSvg.addEventListener('mouseleave', hideChartTooltip);
            marketChartCard.style.display = 'block';
            if (marketPrimaryGrid) {
                marketPrimaryGrid.style.display = 'grid';
            }
            marketExtraGrid.style.display = 'grid';
            renderMarketBars(marketVolumeShell, points, 'volume', `${currentIndex.name} 成交量`);
            renderRsiChart(marketRsiShell, points, indicators.rsi14, currentIndex.name);
            renderMacdChart(marketMacdShell, points, indicators, currentIndex.name);
        }

        async function loadMarketIndices(options = {}) {
            const { silent = false } = options;
            if (autoRefreshState.marketLoading) {
                return;
            }

            autoRefreshState.marketLoading = true;
            if (!silent) {
                setStatus(marketStatus, '正在获取大盘指数数据...');
                indexCards.style.display = 'none';
                marketChartCard.style.display = 'none';
                if (marketPrimaryGrid) {
                    marketPrimaryGrid.style.display = 'none';
                }
                marketExtraGrid.style.display = 'none';
                hideChartTooltip();
            }

            try {
                const response = await fetch(`${BASE_API_URL}/market_indices?days=${marketState.rangeDays}&k_type=day`);
                const result = await response.json();

                if (result.code !== 200) {
                    throw new Error(result.msg);
                }

                marketState.data = result.data;
                marketState.activeKey = marketState.activeKey || result.data.default_index;
                marketMeta.textContent = `数据更新时间：${result.data.updated_at}${result.data.has_realtime ? '（实时指数）' : result.data.is_cached ? '（缓存数据）' : ''}`;
                marketStatus.style.display = 'none';
                renderMarketCards();
                renderMarketChart();
            } catch (error) {
                if (!silent) {
                    setStatus(marketStatus, `大盘指数加载失败：${error.message}`, true);
                    marketMeta.textContent = '当前未获取到指数数据';
                }
            } finally {
                autoRefreshState.marketLoading = false;
            }
        }

        function renderSectorOptions(data) {
            const sectors = data && Array.isArray(data.all_sectors) ? data.all_sectors : [];
            const preferred = data && Array.isArray(data.recommended) ? data.recommended : [];
            const ordered = [];

            preferred.forEach(item => {
                if (item && item.sector_name && !ordered.some(existing => existing.sector_name === item.sector_name)) {
                    ordered.push(item);
                }
            });

            sectors.forEach(item => {
                if (item && item.sector_name && !ordered.some(existing => existing.sector_name === item.sector_name)) {
                    ordered.push(item);
                }
            });

            sectorSelect.innerHTML = '<option value="">请选择板块</option>' + ordered.map(name => `
                <option value="${name.sector_name}" data-code="${name.sector_code || ''}">${name.sector_name}</option>
            `).join('');
            sectorOptionsList.innerHTML = ordered.map(item => `<option value="${item.sector_name}"></option>`).join('');
            sentimentSectorSelect.innerHTML = '<option value="">请选择板块</option>' + ordered.map(item => `
                <option value="${item.sector_name}" data-code="${item.sector_code || ''}">${item.sector_name}</option>
            `).join('');

            if (sectorState.selectedSector) {
                sectorSelect.value = sectorState.selectedSector;
                sectorPickerInput.value = sectorState.selectedSector;
            }
        }

        function syncSectorSelectionByName(sectorName) {
            const targetName = String(sectorName || '').trim();
            if (!targetName) {
                return;
            }

            const sectorOption = Array.from(sectorSelect.options).find(option => option.value === targetName);
            if (sectorOption) {
                sectorSelect.value = targetName;
                sectorPickerInput.value = targetName;
            }

            const sentimentOption = Array.from(sentimentSectorSelect.options).find(option => option.value === targetName);
            if (sentimentOption) {
                sentimentSectorSelect.value = targetName;
                sentimentSectorInput.value = targetName;
            }
        }

        function renderSectorRows(items) {
            if (!items || items.length === 0) {
                sectorBody.innerHTML = '<tr><td colspan="9">当前板块暂无符合条件的股票</td></tr>';
                return;
            }

            sectorBody.innerHTML = items.map(item => `
                <tr>
                    <td>${item.code}</td>
                    <td>${item.name}</td>
                    <td>${item.industry || sectorState.selectedSector || '--'}</td>
                    <td>${item.market || '--'}</td>
                    <td>${item.trade_date || '--'}</td>
                    <td>${formatValue(item.latest_price)}</td>
                    <td class="${getMarketTrendClass(Number(item.change_percent || 0))}">${formatValue(item.change_percent)}%</td>
                    <td class="${getMarketTrendClass(Number(item.change_amount || 0))}">${formatValue(item.change_amount)}</td>
                    <td>${formatInteger(item.volume)}</td>
                </tr>
            `).join('');
        }

        async function loadSectorOptions() {
            setStatus(sectorStatus, '正在获取板块列表...');
            sectorTableWrap.style.display = 'none';
            sectorPagination.style.display = 'none';

            try {
                const response = await fetch(`${BASE_API_URL}/sector_options`);
                const result = await response.json();

                if (result.code !== 200) {
                    throw new Error(result.msg);
                }

                sectorState.loaded = true;
                renderSectorOptions(result.data);
                setSectionMeta(sectorMeta, result.data.updated_at, result.data.source, result.data.warning);
                setStatus(sectorStatus, '请选择一个板块后开始加载当前页股票快照。');
            } catch (error) {
                setStatus(sectorStatus, `板块列表加载失败：${error.message}`, true);
                sectorMeta.textContent = '当前未获取到板块列表';
            }
        }

        async function loadSectorStocks(page = 1) {
            const selectedSector = (sectorPickerInput.value || sectorSelect.value || '').trim();
            syncSectorSelectionByName(selectedSector);
            const selectedOption = sectorSelect.options[sectorSelect.selectedIndex];
            const sectorCode = selectedOption ? (selectedOption.dataset.code || '').trim() : '';
            const keyword = '';

            sectorState.selectedSector = selectedSector;
            sectorState.selectedSectorCode = sectorCode;
            sectorState.keyword = keyword;
            sectorState.page = page;

            if (!selectedSector) {
                setStatus(sectorStatus, '请先选择一个板块。');
                sectorTableWrap.style.display = 'none';
                sectorPagination.style.display = 'none';
                return;
            }

            setStatus(sectorStatus, `正在获取「${selectedSector}」第 ${page} 页股票快照...`);
            sectorTableWrap.style.display = 'none';
            sectorPagination.style.display = 'none';

            try {
                const response = await fetch(`${BASE_API_URL}/sector_stocks?sector_name=${encodeURIComponent(selectedSector)}&sector_code=${encodeURIComponent(sectorCode)}&keyword=${encodeURIComponent(keyword)}&page=${page}&page_size=${SECTOR_PAGE_SIZE}`);
                const result = await response.json();

                if (result.code !== 200) {
                    throw new Error(result.msg);
                }

                const data = result.data;
                setSectionMeta(sectorMeta, data.updated_at, data.source, data.warning);
                if (!data.items || data.items.length === 0) {
                    setStatus(sectorStatus, `「${selectedSector}」当前没有符合条件的股票。`, true);
                    sectorTableWrap.style.display = 'none';
                    sectorPagination.style.display = 'none';
                } else {
                    sectorStatus.style.display = 'none';
                    sectorTableWrap.style.display = 'block';
                    renderSectorRows(data.items);
                    renderPagination(sectorPagination, data.pagination, loadSectorStocks);
                }
            } catch (error) {
                setStatus(sectorStatus, `板块快照加载失败：${error.message}`, true);
            }
        }

        function renderStockDirectoryRows(items) {
            if (!items || items.length === 0) {
                stockDirectoryBody.innerHTML = '<tr><td colspan="9">未找到符合条件的股票</td></tr>';
                return;
            }

            stockDirectoryBody.innerHTML = items.map(item => `
                <tr class="stock-directory-row ${stockChartState.activeCode === item.code ? 'active' : ''}" data-code="${item.code}" data-name="${item.name}">
                    <td>${item.code}</td>
                    <td>${item.name}</td>
                    <td>${item.industry || '--'}</td>
                    <td>${item.market || '--'}</td>
                    <td>${item.trade_date || '--'}</td>
                    <td>${formatValue(item.latest_price)}</td>
                    <td class="${getMarketTrendClass(Number(item.change_percent || 0))}">${formatValue(item.change_percent)}%</td>
                    <td class="${getMarketTrendClass(Number(item.change_amount || 0))}">${formatValue(item.change_amount)}</td>
                    <td>${formatValue(item.turnover_rate)}%</td>
                </tr>
            `).join('');
        }

        async function loadStockDirectory(page = 1, options = {}) {
            const { silent = false } = options;
            if (autoRefreshState.stockLoading) {
                return;
            }

            stockDirectoryState.page = page;
            stockDirectoryState.keyword = stockSearchInput.value.trim();
            if (!stockDirectoryState.keyword) {
                setStatus(stockDirectoryStatus, '请输入一个或多个股票代码或名称后查询盘中实时行情。');
                stockDirectoryMeta.textContent = '支持多支股票同时检索，空格、逗号、顿号、换行都可以分隔。';
                stockDirectoryTableWrap.style.display = 'none';
                stockDirectoryPagination.style.display = 'none';
                stockChartCard.style.display = 'none';
                return;
            }

            autoRefreshState.stockLoading = true;
            if (!silent) {
                setStatus(stockDirectoryStatus, '正在获取个股实时行情...');
                stockDirectoryTableWrap.style.display = 'none';
                stockDirectoryPagination.style.display = 'none';
            }

            try {
                const response = await fetch(`${BASE_API_URL}/stock_directory?page=${page}&page_size=${STOCK_PAGE_SIZE}&keyword=${encodeURIComponent(stockDirectoryState.keyword)}`);
                const result = await response.json();

                if (result.code !== 200) {
                    throw new Error(result.msg);
                }

                const data = result.data;
                setSectionMeta(stockDirectoryMeta, data.updated_at, data.source, data.warning);
                if (!data.items || data.items.length === 0) {
                    setStatus(stockDirectoryStatus, '未找到符合条件的股票，请换一个代码或名称试试。', true);
                    stockDirectoryTableWrap.style.display = 'none';
                    stockDirectoryPagination.style.display = 'none';
                    stockChartCard.style.display = 'none';
                } else {
                    stockDirectoryStatus.style.display = 'none';
                    stockDirectoryTableWrap.style.display = 'block';
                    renderStockDirectoryRows(data.items);
                    renderPagination(stockDirectoryPagination, data.pagination, loadStockDirectory);
                    const activeItem = data.items.find(item => item.code === stockChartState.activeCode) || data.items[0];
                    loadStockCharts(activeItem.code, activeItem.name, { silent: true });
                }
            } catch (error) {
                if (!silent) {
                    setStatus(stockDirectoryStatus, `个股实时行情加载失败：${error.message}`, true);
                    stockDirectoryMeta.textContent = '当前未获取到个股实时行情';
                }
            } finally {
                autoRefreshState.stockLoading = false;
            }
        }

        async function predictStock(days) {
            if (!getCurrentUserId()) {
                showPredictResult('<p class="alert-error">请先登录后再执行分析。</p>', false);
                authOverlay.style.display = 'flex';
                return;
            }
            const stockCodes = parseStockCodesInput(stockCodeInput.value);
            const selectedCases = getSelectedPredictCases();

            if (stockCodes.length === 0) {
                showPredictResult('<p class="alert-error">请先输入股票代码！</p>', false);
                return;
            }
            if (stockCodes.some(code => isNaN(code))) {
                showPredictResult('<p class="alert-error">股票代码必须为数字！</p>', false);
                return;
            }
            if (selectedCases.length === 0) {
                showPredictResult('<p class="alert-error">请至少选择一个分析指标！</p>', false);
                return;
            }

            let predictSucceeded = false;
            try {
                startAnalysisProgress();

                const rows = [];
                for (const stockCode of stockCodes) {
                    const response = await fetch(`${BASE_API_URL}/predict_stock`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            user_id: getCurrentUserId(),
                            stock_code: stockCode,
                            days: days,
                            selected_cases: selectedCases,
                            risk_preference: getRiskPreferencePayload()
                        })
                    });
                    const result = await response.json();
                    if (result.code === 200) {
                        const data = result.data;
                        generatedReportState[stockCode] = data.report_context || null;
                        const updateSummary = data.update_summary || {};
                        const reportHtml = escapeHtmlAttribute(data.report_html || '');
                        rows.push(`
                            <p class="alert-success">${stockCode}：分析成功</p>
                            <p>历史数据：${updateSummary.data_count || '--'} 条，范围 ${updateSummary.date_range || '--'}，来源 ${updateSummary.data_source_label || updateSummary.data_source || '--'}</p>
                            <p>分析天数：${data.predict_days}天</p>
                            <p>指标：${(data.selected_case_labels || []).join('、')}</p>
                            <div class="generated-report-preview">
                                <iframe title="${stockCode} 报告预览" srcdoc="${reportHtml}"></iframe>
                            </div>
                            ${buildLlmDebugBlock(data.report_context || {})}
                            <details class="debug-json-wrap">
                                <summary>调试 JSON</summary>
                                <pre>${JSON.stringify(data, null, 2)}</pre>
                            </details>
                        `);
                    } else {
                        rows.push(`<p class="alert-error">${stockCode}：${result.msg}</p>`);
                    }
                }
                showPredictResult(rows.join(''), true);
                predictSucceeded = true;
                await loadHistoryReports();
            } catch (error) {
                showPredictResult(`<p class="alert-error">预测请求失败：${error.message}</p>`, false);
                stopAnalysisProgress(false);
            } finally {
                if (analysisProgress.style.display !== 'none' && typeof predictSucceeded !== 'undefined' && predictSucceeded) {
                    stopAnalysisProgress(true);
                }
            }
        }

        async function predictMarketIndex(days) {
            if (!getCurrentUserId()) {
                showMarketPredictResult('<p class="alert-error">请先登录后再执行分析。</p>', false);
                authOverlay.style.display = 'flex';
                return;
            }
            const indexKey = marketAnalysisIndexSelect ? marketAnalysisIndexSelect.value.trim() : '';
            const selectedCases = getSelectedMarketPredictCases();
            if (!indexKey) {
                showMarketPredictResult('<p class="alert-error">请先选择一个大盘指数！</p>', false);
                return;
            }
            if (selectedCases.length === 0) {
                showMarketPredictResult('<p class="alert-error">请至少选择一个分析指标！</p>', false);
                return;
            }

            let predictSucceeded = false;
            try {
                if (marketAnalysisProgress) {
                    marketAnalysisProgress.style.display = 'block';
                }
                if (marketAnalysisProgressText) {
                    marketAnalysisProgressText.textContent = '正在生成大盘分析报告...';
                }
                const response = await fetch(`${BASE_API_URL}/predict_market_index`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        user_id: getCurrentUserId(),
                        index_key: indexKey,
                        days: days,
                        selected_cases: selectedCases,
                        risk_preference: getRiskPreferencePayload()
                    })
                });
                const result = await response.json();
                if (result.code !== 200) {
                    throw new Error(result.msg);
                }
                const data = result.data || {};
                const updateSummary = data.update_summary || {};
                const reportHtml = escapeHtmlAttribute(data.report_html || '');
                showMarketPredictResult(`
                    <p class="alert-success">${escapeHtml(data.stock_name || indexKey)}：分析成功</p>
                    <p>历史数据：${updateSummary.data_count || '--'} 条，范围 ${updateSummary.date_range || '--'}，来源 ${updateSummary.data_source_label || '--'}</p>
                    <p>分析天数：${data.predict_days}天</p>
                    <p>指标：${(data.selected_case_labels || []).join('、')}</p>
                    <div class="generated-report-preview">
                        <iframe title="${escapeHtmlAttribute(data.stock_name || indexKey)} 报告预览" srcdoc="${reportHtml}"></iframe>
                    </div>
                    ${buildLlmDebugBlock(data.report_context || {})}
                    <details class="debug-json-wrap">
                        <summary>调试 JSON</summary>
                        <pre>${JSON.stringify(data, null, 2)}</pre>
                    </details>
                `, true);
                predictSucceeded = true;
                await loadHistoryReports();
            } catch (error) {
                showMarketPredictResult(`<p class="alert-error">大盘分析请求失败：${error.message}</p>`, false);
                if (marketAnalysisProgressText) {
                    marketAnalysisProgressText.textContent = '大盘分析生成失败';
                }
            } finally {
                if (marketAnalysisProgress) {
                    if (predictSucceeded && marketAnalysisProgressText) {
                        marketAnalysisProgressText.textContent = '大盘分析生成完成';
                    }
                    window.setTimeout(() => {
                        marketAnalysisProgress.style.display = 'none';
                    }, 900);
                }
            }
        }

        async function sendReport() {
            if (!getCurrentUserId()) {
                showReportResult('<p class="alert-error">请先登录后再发送报告。</p>', false);
                return;
            }
            const stockCodes = parseStockCodesInput(stockCodeInput.value);
            if (stockCodes.length === 0) {
                showReportResult('<p class="alert-error">请先输入股票代码！</p>', false);
                return;
            }
            if (stockCodes.some(code => isNaN(code))) {
                showReportResult('<p class="alert-error">股票代码必须为数字！</p>', false);
                return;
            }

            showReportResult('<p>正在批量发送 HTML 报告，请稍候...</p>', true);

            try {
                const rows = [];
                for (const stockCode of stockCodes) {
                    const reportContext = generatedReportState[stockCode] || null;
                    if (!reportContext) {
                        rows.push(`<p class="alert-error">${stockCode}：请先执行分析并生成报告后再发送。</p>`);
                        continue;
                    }
                    const response = await fetch(`${BASE_API_URL}/send_report`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ user_id: getCurrentUserId(), stock_code: stockCode, report_context: reportContext })
                    });
                    const result = await response.json();
                    if (result.code === 200) {
                        const data = result.data || {};
                        rows.push(`
                            <p class="alert-success">${stockCode}：${result.msg}</p>
                            <p>发送邮箱：${data.email || '--'}</p>
                            <p>邮件主题：${data.subject || '--'}</p>
                        `);
                    } else {
                        rows.push(`<p class="alert-error">${stockCode}：${result.msg}</p>`);
                    }
                }
                showReportResult(rows.join(''), true);
            } catch (error) {
                showReportResult(`<p class="alert-error">发送请求失败：${error.message}</p>`, false);
            }
        }

        async function getStockList() {
            try {
                const userId = getCurrentUserId();
                if (!userId) {
                    return [];
                }
                const response = await fetch(`${BASE_API_URL}/get_stocks?user_id=${userId}`);
                const result = await response.json();
                if (result.code !== 200) {
                    showSettingsStockAlert(result.msg, false);
                    return [];
                }
                return result.data;
            } catch (error) {
                showSettingsStockAlert('获取自选股失败：' + error.message, false);
                return [];
            }
        }

        async function loadProfileSettings() {
            if (!getCurrentUserId() || !profileUsernameInput) {
                return;
            }
            setProfileStatus('正在读取用户资料...');
            try {
                const response = await fetch(`${BASE_API_URL}/user_settings/profile?user_id=${getCurrentUserId()}`);
                const result = await response.json();
                if (result.code !== 200) {
                    throw new Error(result.msg);
                }
                const user = result.data?.user || currentUser || {};
                profileUsernameInput.value = user.username || '';
                persistCurrentUser({ ...(currentUser || {}), ...user });
                renderUserAvatar(profileAvatarPreview, currentUser);
                setProfileStatus('已加载当前用户资料。');
            } catch (error) {
                setProfileStatus(`用户资料读取失败：${error.message}`, 'error');
            }
        }

        async function loadReportEmailSettings() {
            setEmailStatus('正在读取当前邮箱设置...');

            try {
                const response = await fetch(`${BASE_API_URL}/user_settings/email?user_id=${getCurrentUserId()}`);
                const result = await response.json();
                if (result.code !== 200) {
                    throw new Error(result.msg);
                }

                const email = result.data && result.data.email ? result.data.email : '';
                reportEmailInput.value = email;
                settingsState.loaded = true;
                setEmailStatus(email ? `当前已保存邮箱：${email}` : '当前还没有设置邮箱。');
            } catch (error) {
                setEmailStatus(`邮箱设置读取失败：${error.message}`, 'error');
            }
        }

        async function loadLlmPromptSettings() {
            setLlmPromptStatus('正在读取 LLM Prompt 设置...');

            try {
                const response = await fetch(`${BASE_API_URL}/user_settings/llm_prompts?user_id=${getCurrentUserId()}`);
                const result = await response.json();
                if (result.code !== 200) {
                    throw new Error(result.msg);
                }
                llmSystemPromptInput.value = result.data.system_prompt || '';
                llmUserPromptInput.value = result.data.user_prompt || '';
                setLlmPromptStatus('已加载当前 Prompt 设置。');
            } catch (error) {
                setLlmPromptStatus(`Prompt 设置读取失败：${error.message}`, 'error');
            }
        }

        async function loadReportScheduleSettings() {
            setReportScheduleStatus('正在读取定时发送设置...');

            try {
                const response = await fetch(`${BASE_API_URL}/user_settings/report_schedule?user_id=${getCurrentUserId()}`);
                const result = await response.json();
                if (result.code !== 200) {
                    throw new Error(result.msg);
                }

                const data = result.data || {};
                reportScheduleEnabledInput.checked = Boolean(data.enabled);
                reportScheduleTimeInput.value = data.time || '09:00';
                settingsState.reportScheduleSelectedCodes = Array.isArray(data.stock_codes) ? data.stock_codes.slice() : [];
                renderReportScheduleStockOptions(await getStockList());
                const summary = data.enabled
                    ? `当前已开启定时发送，时间 ${data.time || '09:00'}，共 ${settingsState.reportScheduleSelectedCodes.length} 只股票。`
                    : '当前未开启定时发送。';
                setReportScheduleStatus(summary);
            } catch (error) {
                setReportScheduleStatus(`定时发送设置读取失败：${error.message}`, 'error');
            }
        }

        function renderSentimentItems(items) {
            if (!items || items.length === 0) {
                sentimentList.style.display = 'none';
                sentimentPagination.style.display = 'none';
                setStatus(sentimentStatus, '当前时间范围内暂无可展示的舆情。');
                return;
            }

            sentimentState.currentItems = items.slice();
            const total = sentimentState.currentItems.length;
            const totalPages = Math.max(1, Math.ceil(total / sentimentState.pageSize));
            sentimentState.page = Math.min(Math.max(1, sentimentState.page), totalPages);
            const start = (sentimentState.page - 1) * sentimentState.pageSize;
            const pageItems = sentimentState.currentItems.slice(start, start + sentimentState.pageSize);

            sentimentList.innerHTML = pageItems.map(item => `
                <article class="sentiment-item">
                    <div class="sentiment-item-head">
                        <div class="sentiment-item-title">${item.title || '未命名资讯'}</div>
                        <div class="sentiment-item-time">${item.publish_time || '--'}</div>
                    </div>
                    <div class="sentiment-item-summary">${item.summary || '暂无摘要'}</div>
                    <div class="sentiment-item-meta">
                        <span class="sentiment-pill ${getSentimentSourceClass(item.source)}">来源：${item.source || '未知来源'}</span>
                        <span class="sentiment-pill sentiment-pill-tag">标签：${item.tag || '舆情'}</span>
                        ${item.url ? `<a class="sentiment-link" href="${item.url}" target="_blank" rel="noopener noreferrer">查看原文</a>` : ''}
                    </div>
                </article>
            `).join('');
            sentimentStatus.style.display = 'none';
            sentimentList.style.display = 'grid';
            renderPagination(sentimentPagination, {
                total: total,
                page: sentimentState.page,
                total_pages: totalPages
            }, function(page) {
                sentimentState.page = page;
                renderSentimentItems(sentimentState.currentItems);
            });
        }

        async function loadSentimentSectorOptions() {
            try {
                if (!sectorState.loaded) {
                    await loadSectorOptions();
                }
                sentimentState.sectorOptionsLoaded = true;
            } catch (error) {
                sentimentMeta.textContent = `板块列表加载失败：${error.message}`;
            }
        }

        async function fetchSentimentData(url, token) {
            const response = await fetch(url, { cache: 'no-store' });
            const result = await response.json();
            if (token !== sentimentState.requestToken) {
                return null;
            }
            if (result.code !== 200) {
                throw new Error(result.msg);
            }
            return result.data || {};
        }

        function applySentimentData(data, metaText, { resetPage = false, mode = sentimentState.mode } = {}) {
            if (!data) {
                return;
            }
            if (resetPage) {
                sentimentState.page = 1;
            }
            const suffix = data.is_preview ? ` | 首屏预览 ${Math.min(data.preview_limit || 10, (data.items || []).length)} 条，正在继续补全...` : '';
            const nextMetaText = `${metaText}${suffix}`;
            sentimentState.cache[mode] = {
                metaText: nextMetaText,
                items: data.items || []
            };
            if (sentimentState.mode === mode) {
                sentimentMeta.textContent = nextMetaText;
                renderSentimentItems(data.items || []);
            }
        }

        async function loadMarketSentiment() {
            const token = Date.now();
            sentimentState.requestToken = token;
            const isActiveMode = sentimentState.mode === 'market';
            if (isActiveMode) {
                setStatus(sentimentStatus, '正在获取大盘舆情...');
                sentimentList.style.display = 'none';
                sentimentPagination.style.display = 'none';
            }
            try {
                syncMarketSentimentRange();
                const { startTime, endTime } = parseSentimentRange(sentimentStartTimeInput, sentimentEndTimeInput, 3 / 24);
                const baseMeta = '范围：近 3 小时';
                const previewData = await fetchSentimentData(`${BASE_API_URL}/sentiment/market?days=1&stage=preview&start_time=${encodeURIComponent(startTime)}&end_time=${encodeURIComponent(endTime)}&_=${Date.now()}`, token);
                if (!previewData) {
                    return;
                }
                applySentimentData(previewData, `${baseMeta} | 来源：${previewData.source} | 更新时间：${previewData.updated_at}`, { resetPage: true, mode: 'market' });
                const fullData = await fetchSentimentData(`${BASE_API_URL}/sentiment/market?days=1&stage=full&start_time=${encodeURIComponent(startTime)}&end_time=${encodeURIComponent(endTime)}&_=${Date.now()}`, token);
                if (!fullData) {
                    return;
                }
                applySentimentData(fullData, `${baseMeta} | 来源：${fullData.source} | 更新时间：${fullData.updated_at}`, { resetPage: true, mode: 'market' });
            } catch (error) {
                if (isActiveMode) {
                    setStatus(sentimentStatus, `大盘舆情获取失败：${error.message}`, true);
                }
            }
        }

        async function loadSectorSentiment() {
            const sectorName = (sentimentSectorInput.value || sentimentSectorSelect.value || '').trim();
            if (!sectorName) {
                setStatus(sentimentStatus, '请先输入板块名。', true);
                return;
            }

            const token = Date.now();
            sentimentState.requestToken = token;
            setStatus(sentimentStatus, `正在获取「${sectorName}」舆情...`);
            sentimentList.style.display = 'none';
            sentimentPagination.style.display = 'none';
            try {
                const { startTime, endTime } = parseSentimentRange(sentimentSectorStartTimeInput, sentimentSectorEndTimeInput, 4);
                const baseMeta = `板块：${sectorName}`;
                const previewData = await fetchSentimentData(`${BASE_API_URL}/sentiment/sector?sector_name=${encodeURIComponent(sectorName)}&days=4&stage=preview&start_time=${encodeURIComponent(startTime)}&end_time=${encodeURIComponent(endTime)}&_=${Date.now()}`, token);
                if (!previewData) {
                    return;
                }
                applySentimentData(previewData, `${baseMeta} | 范围：${previewData.date_range.join(' 至 ')} | 更新时间：${previewData.updated_at}`, { resetPage: true, mode: 'sector' });
                const fullData = await fetchSentimentData(`${BASE_API_URL}/sentiment/sector?sector_name=${encodeURIComponent(sectorName)}&days=4&stage=full&start_time=${encodeURIComponent(startTime)}&end_time=${encodeURIComponent(endTime)}&_=${Date.now()}`, token);
                if (!fullData) {
                    return;
                }
                applySentimentData(fullData, `${baseMeta} | 范围：${fullData.date_range.join(' 至 ')} | 更新时间：${fullData.updated_at}`, { resetPage: true, mode: 'sector' });
            } catch (error) {
                setStatus(sentimentStatus, `板块舆情获取失败：${error.message}`, true);
            }
        }

        async function loadStockSentiment() {
            const stockCode = sentimentStockCodeInput.value.trim();
            if (!stockCode) {
                setStatus(sentimentStatus, '请输入至少一个股票代码。', true);
                return;
            }

            const token = Date.now();
            sentimentState.requestToken = token;
            const isActiveMode = sentimentState.mode === 'stock';
            if (isActiveMode) {
                setStatus(sentimentStatus, `正在获取「${stockCode}」舆情...`);
                sentimentList.style.display = 'none';
                sentimentPagination.style.display = 'none';
            }
            try {
                const { startTime, endTime } = parseSentimentRange(sentimentStockStartTimeInput, sentimentStockEndTimeInput, 7);
                const baseMeta = `个股：${stockCode}`;
                const previewData = await fetchSentimentData(`${BASE_API_URL}/sentiment/stock?stock_code=${encodeURIComponent(stockCode)}&days=7&stage=preview&start_time=${encodeURIComponent(startTime)}&end_time=${encodeURIComponent(endTime)}&_=${Date.now()}`, token);
                if (!previewData) {
                    return;
                }
                applySentimentData(previewData, `${baseMeta} | 范围：${previewData.date_range.join(' 至 ')} | 更新时间：${previewData.updated_at}`, { resetPage: true, mode: 'stock' });
                const fullData = await fetchSentimentData(`${BASE_API_URL}/sentiment/stock?stock_code=${encodeURIComponent(stockCode)}&days=7&stage=full&start_time=${encodeURIComponent(startTime)}&end_time=${encodeURIComponent(endTime)}&_=${Date.now()}`, token);
                if (!fullData) {
                    return;
                }
                applySentimentData(fullData, `${baseMeta} | 范围：${fullData.date_range.join(' 至 ')} | 更新时间：${fullData.updated_at}`, { resetPage: true, mode: 'stock' });
            } catch (error) {
                if (isActiveMode) {
                    setStatus(sentimentStatus, `个股舆情获取失败：${error.message}`, true);
                }
            }
        }

        async function autoLoadInitialSentiment() {
            if (sentimentState.initialAutoLoaded || !getCurrentUserId()) {
                return;
            }
            sentimentState.initialAutoLoaded = true;
            try {
                syncMarketSentimentRange();
                await loadMarketSentiment();

                const stocks = await getStockList();
                const stockCodes = stocks
                    .map(item => String(item.stock_code || '').trim())
                    .filter(Boolean);
                if (!stockCodes.length) {
                    return;
                }
                syncStockSentimentRange();
                sentimentStockCodeInput.value = stockCodes.join(' ');
                await loadStockSentiment();
            } catch (error) {
                console.warn('自动舆情加载失败', error);
            }
        }

        async function saveProfileSettings() {
            if (!getCurrentUserId()) {
                setProfileStatus('请先登录后再修改资料。', 'error');
                return;
            }
            const username = (profileUsernameInput?.value || '').trim();
            if (!username) {
                setProfileStatus('请输入用户名后再保存。', 'error');
                return;
            }

            setProfileStatus('正在保存用户资料...');
            try {
                const formData = new FormData();
                formData.append('user_id', String(getCurrentUserId()));
                formData.append('username', username);
                const avatarFile = profileAvatarInput?.files && profileAvatarInput.files[0] ? profileAvatarInput.files[0] : null;
                if (avatarFile) {
                    formData.append('avatar', avatarFile);
                }
                const response = await fetch(`${BASE_API_URL}/user_settings/profile`, {
                    method: 'POST',
                    body: formData
                });
                const result = await response.json();
                if (result.code !== 200) {
                    throw new Error(result.msg);
                }
                const user = result.data?.user || {};
                persistCurrentUser({ ...(currentUser || {}), ...user });
                if (profileAvatarInput) {
                    profileAvatarInput.value = '';
                }
                if (profileUsernameInput) {
                    profileUsernameInput.value = currentUser.username || username;
                }
                renderUserAvatar(profileAvatarPreview, currentUser);
                setProfileStatus('用户资料保存成功。', 'success');
                forumState.loaded = false;
                await loadForumPosts();
            } catch (error) {
                setProfileStatus(`用户资料保存失败：${error.message}`, 'error');
            }
        }

        async function saveReportEmailSettings() {
            const email = reportEmailInput.value.trim();
            if (!email) {
                setEmailStatus('请输入邮箱地址后再保存。', 'error');
                return;
            }

            setEmailStatus('正在保存邮箱设置...');

            try {
                const response = await fetch(`${BASE_API_URL}/user_settings/email`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_id: getCurrentUserId(), email: email })
                });
                const result = await response.json();
                if (result.code !== 200) {
                    throw new Error(result.msg);
                }

                reportEmailInput.value = result.data.email || email;
                settingsState.loaded = true;
                setEmailStatus(`邮箱保存成功：${reportEmailInput.value}`, 'success');
            } catch (error) {
                setEmailStatus(`邮箱保存失败：${error.message}`, 'error');
            }
        }

        async function saveLlmPromptSettings() {
            const systemPrompt = llmSystemPromptInput.value.trim();
            const userPrompt = llmUserPromptInput.value.trim();
            if (!systemPrompt || !userPrompt) {
                setLlmPromptStatus('System Prompt 和 User Prompt 都不能为空。', 'error');
                return;
            }

            setLlmPromptStatus('正在保存 Prompt 设置...');

            try {
                const response = await fetch(`${BASE_API_URL}/user_settings/llm_prompts`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_id: getCurrentUserId(), system_prompt: systemPrompt, user_prompt: userPrompt })
                });
                const result = await response.json();
                if (result.code !== 200) {
                    throw new Error(result.msg);
                }
                llmSystemPromptInput.value = result.data.system_prompt || systemPrompt;
                llmUserPromptInput.value = result.data.user_prompt || userPrompt;
                setLlmPromptStatus('Prompt 保存成功。', 'success');
            } catch (error) {
                setLlmPromptStatus(`Prompt 保存失败：${error.message}`, 'error');
            }
        }

        async function saveReportScheduleSettings() {
            const enabled = Boolean(reportScheduleEnabledInput && reportScheduleEnabledInput.checked);
            const scheduleTime = (reportScheduleTimeInput && reportScheduleTimeInput.value ? reportScheduleTimeInput.value : '').trim();
            const stockCodes = getSelectedScheduleStockCodes();
            if (!scheduleTime) {
                setReportScheduleStatus('请选择定时发送时间。', 'error');
                return;
            }
            if (enabled && stockCodes.length === 0) {
                setReportScheduleStatus('开启定时发送时，请至少选择一只股票。', 'error');
                return;
            }

            setReportScheduleStatus('正在保存定时发送设置...');

            try {
                const response = await fetch(`${BASE_API_URL}/user_settings/report_schedule`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        user_id: getCurrentUserId(),
                        enabled: enabled,
                        time: scheduleTime,
                        stock_codes: stockCodes
                    })
                });
                const result = await response.json();
                if (result.code !== 200) {
                    throw new Error(result.msg);
                }

                const data = result.data || {};
                reportScheduleEnabledInput.checked = Boolean(data.enabled);
                reportScheduleTimeInput.value = data.time || scheduleTime;
                settingsState.reportScheduleSelectedCodes = Array.isArray(data.stock_codes) ? data.stock_codes.slice() : stockCodes.slice();
                renderReportScheduleStockOptions(await getStockList());
                const summary = data.enabled
                    ? `定时发送已开启：每天 ${data.time || scheduleTime} 发送 ${settingsState.reportScheduleSelectedCodes.length} 只股票报告。`
                    : '定时发送已关闭。';
                setReportScheduleStatus(summary, 'success');
            } catch (error) {
                setReportScheduleStatus(`定时发送设置保存失败：${error.message}`, 'error');
            }
        }

        function populateFavoriteStockSelects(stocks) {
            const options = stocks.map(stock => `
                <option value="${stock.stock_code}">${stock.stock_code} ${stock.stock_name}</option>
            `).join('');
            favoriteStockSelect.innerHTML = '<option value="">从自选股中选择</option>' + options;
            stockDirectoryFavoriteSelect.innerHTML = '<option value="">从自选股中选择</option>' + options;
            sentimentFavoriteStockSelect.innerHTML = '<option value="">从自选股中选择</option>' + options;
            renderReportScheduleStockOptions(stocks);
        }

        async function renderManagedStockList() {
            const stocks = await getStockList();
            populateFavoriteStockSelects(stocks);
            settingsStockList.innerHTML = '';

            if (stocks.length === 0) {
                settingsStockList.innerHTML = '<p class="tip">暂无自选股，添加后可在个股分析和舆情分析中直接选择。</p>';
                settingsStockToggleMeta.textContent = '暂无内容';
                return;
            }

            settingsStockToggleMeta.textContent = `共 ${stocks.length} 只`;

            stocks.forEach(stock => {
                const item = document.createElement('div');
                item.className = 'stock-item';
                item.innerHTML = `
                    <span class="stock-item-info">
                        <span class="stock-item-code">${stock.stock_code}</span>
                        <span class="stock-item-name">${stock.stock_name}</span>
                    </span>
                    <span class="delete-btn" data-code="${stock.stock_code}">删除</span>
                `;
                settingsStockList.appendChild(item);
            });
        }

        async function loadManagedStocks() {
            await renderManagedStockList();
            settingsState.stocksLoaded = true;
            await loadFavoriteSnapshot();
        }

        async function deleteManagedStock(stockCode) {
            try {
                const response = await fetch(`${BASE_API_URL}/delete_stock`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_id: getCurrentUserId(), stock_code: stockCode })
                });
                const result = await response.json();
                if (result.code === 200) {
                    showSettingsStockAlert(result.msg);
                    await loadManagedStocks();
                    await loadHistoryReports();
                } else {
                    showSettingsStockAlert(result.msg, false);
                }
            } catch (error) {
                showSettingsStockAlert('删除失败：' + error.message, false);
            }
        }

        async function addManagedStock() {
            const code = settingsAddStockCodeInput.value.trim();
            const name = settingsAddStockNameInput.value.trim();

            if (!code && !name) {
                showSettingsStockAlert('请至少输入股票代码或股票名称！', false);
                return;
            }
            if (code && isNaN(code)) {
                showSettingsStockAlert('股票代码必须为数字！', false);
                return;
            }

            try {
                const response = await fetch(`${BASE_API_URL}/add_stock`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_id: getCurrentUserId(), stock_code: code, stock_name: name })
                });
                const result = await response.json();
                if (result.code === 200) {
                    showSettingsStockAlert(result.msg);
                    settingsAddStockCodeInput.value = '';
                    settingsAddStockNameInput.value = '';
                    await loadManagedStocks();
                    await loadHistoryReports();
                } else {
                    showSettingsStockAlert(result.msg, false);
                }
            } catch (error) {
                showSettingsStockAlert('添加失败：' + error.message, false);
            }
        }

        function appendSentimentFavoriteStock() {
            const stockCode = sentimentFavoriteStockSelect.value.trim();
            if (!stockCode) {
                return;
            }
            const currentCodes = sentimentStockCodeInput.value.trim();
            const existing = currentCodes ? currentCodes.split(/\s+/) : [];
            if (!existing.includes(stockCode)) {
                sentimentStockCodeInput.value = currentCodes ? `${currentCodes} ${stockCode}` : stockCode;
            }
        }

        async function loadAllFavoriteStockSentiment() {
            const stocks = await getStockList();
            const stockCodes = stocks
                .map(item => String(item.stock_code || '').trim())
                .filter(Boolean);
            if (!stockCodes.length) {
                setStatus(sentimentStatus, '暂无自选股，请先在设置中添加。', true);
                return;
            }
            syncStockSentimentRange();
            sentimentStockCodeInput.value = stockCodes.join(' ');
            await loadStockSentiment();
        }

        function appendStockDirectoryFavorite() {
            const stockCode = stockDirectoryFavoriteSelect.value.trim();
            if (!stockCode) {
                return;
            }
            const currentCodes = stockSearchInput.value.trim();
            const existing = currentCodes ? currentCodes.split(/\s+/) : [];
            if (!existing.includes(stockCode)) {
                stockSearchInput.value = currentCodes ? `${currentCodes} ${stockCode}` : stockCode;
            }
        }

        menuItems.forEach(item => {
            item.addEventListener('click', function() {
                if (this.id === 'stockMenuToggle') {
                    const nextOpen = !stockSubmenu?.classList.contains('open');
                    stockSubmenu?.classList.toggle('open', nextOpen);
                    stockMenuToggle?.setAttribute('aria-expanded', nextOpen ? 'true' : 'false');
                    if (nextOpen) {
                        switchPanel('stockMarketPanel');
                        applyStockPanelMode('market');
                    }
                    return;
                }
                switchPanel(this.dataset.panel);
            });
        });

        sentimentTabs.forEach(tab => {
            tab.addEventListener('click', function() {
                switchSentimentMode(this.dataset.sentimentPanel);
            });
        });
        forumTabs.forEach(tab => {
            tab.addEventListener('click', function() {
                switchForumPanel(this.dataset.forumPanel);
            });
        });

        reloadMarketBtn.addEventListener('click', loadMarketIndices);
        chartPeriodButtons.forEach(button => {
            button.addEventListener('click', function() {
                const nextPeriod = Number(this.dataset.range || 365);
                if (nextPeriod === marketState.rangeDays) {
                    return;
                }
                setChartPeriod(nextPeriod);
                loadMarketIndices();
            });
        });
        stockChartTypeButtons.forEach(button => {
            button.addEventListener('click', function() {
                const nextType = this.dataset.chartType || 'candlestick';
                if (nextType === stockChartState.activeType) {
                    return;
                }
                setStockChartType(nextType);
                renderStockChart();
            });
        });
        stockChartRangeButtons.forEach(button => {
            button.addEventListener('click', function() {
                const nextRange = Number(this.dataset.range || 365);
                if (nextRange === stockChartState.rangeDays) {
                    return;
                }
                setStockChartRange(nextRange);
                if (stockChartState.activeCode) {
                    loadStockCharts(stockChartState.activeCode, stockChartState.activeName);
                }
            });
        });
        marketRefreshInterval.addEventListener('change', function() {
            startMarketAutoRefresh();
            loadMarketIndices({ silent: true });
        });

        sectorSelect.addEventListener('change', function() {
            sectorPickerInput.value = this.value;
            if (this.value.trim()) {
                loadSectorStocks(1);
            } else {
                setStatus(sectorStatus, '请先选择一个板块。');
                sectorTableWrap.style.display = 'none';
                sectorPagination.style.display = 'none';
            }
        });

        sectorPickerInput.addEventListener('change', function() {
            syncSectorSelectionByName(this.value);
        });

        sectorSearchBtn.addEventListener('click', function() {
            loadSectorStocks(1);
        });

        sectorResetBtn.addEventListener('click', function() {
            sectorPickerInput.value = '';
            sectorSelect.value = '';
            sectorState.selectedSector = '';
            sectorState.selectedSectorCode = '';
            sectorState.keyword = '';
            sectorState.page = 1;
            sectorTableWrap.style.display = 'none';
            sectorPagination.style.display = 'none';
            setStatus(sectorStatus, '请选择一个板块后开始加载当前页股票快照。');
        });

        sectorPickerInput.addEventListener('keydown', function(event) {
            if (event.key === 'Enter') {
                loadSectorStocks(1);
            }
        });

        stockSearchBtn.addEventListener('click', function() {
            loadStockDirectory(1);
        });

        stockRefreshInterval.addEventListener('change', function() {
            startStockAutoRefresh();
            if (stockDirectoryState.keyword) {
                loadStockDirectory(stockDirectoryState.page, { silent: true });
            }
        });

        stockSearchInput.addEventListener('keydown', function(event) {
            if (event.key === 'Enter') {
                loadStockDirectory(1);
            }
        });
        stockDirectoryBody.addEventListener('click', function(event) {
            const row = event.target.closest('.stock-directory-row');
            if (!row) {
                return;
            }
            loadStockCharts(row.dataset.code || '', row.dataset.name || '');
        });
        stockDirectoryFavoriteSelect.addEventListener('change', appendStockDirectoryFavorite);
        stockSubmenuItems.forEach(item => {
            item.addEventListener('click', function() {
                switchPanel(this.dataset.stockMode === 'report' ? 'stockReportPanel' : 'stockMarketPanel');
                applyStockPanelMode(this.dataset.stockMode);
            });
        });
        authSwitchBtn.addEventListener('click', function() {
            setAuthMode(authState.mode === 'login' ? 'register' : 'login');
        });
        if (authForgotBtn) {
            authForgotBtn.addEventListener('click', function() {
                setAuthMode('forgot');
            });
        }
        authSubmitBtn.addEventListener('click', submitAuth);
        if (sendEmailCodeBtn) {
            sendEmailCodeBtn.addEventListener('click', sendAuthEmailCode);
        }
        authPasswordInput.addEventListener('keydown', function(event) {
            if (event.key === 'Enter') {
                submitAuth();
            }
        });
        logoutBtn.addEventListener('click', logout);

        favoriteStockSelect.addEventListener('change', function() {
            const selectedValue = this.value.trim();
            if (selectedValue) {
                const currentCodes = stockCodeInput.value.trim();
                const existing = currentCodes ? currentCodes.split(/\s+/) : [];
                if (!existing.includes(selectedValue)) {
                    stockCodeInput.value = currentCodes ? `${currentCodes} ${selectedValue}` : selectedValue;
                }
            }
        });

        settingsAddStockBtn.addEventListener('click', addManagedStock);
        settingsAddStockNameInput.addEventListener('keydown', function(event) {
            if (event.key === 'Enter') {
                addManagedStock();
            }
        });
        settingsAddStockCodeInput.addEventListener('keydown', function(event) {
            if (event.key === 'Enter') {
                addManagedStock();
            }
        });
        settingsStockToggleBtn.addEventListener('click', function() {
            setManagedStocksExpanded(!settingsState.stockListExpanded);
        });
        settingsStockList.addEventListener('click', function(event) {
            const target = event.target;
            if (target.classList.contains('delete-btn')) {
                const stockCode = target.getAttribute('data-code');
                if (!confirm(`确定要删除 ${stockCode} 吗？`)) return;
                deleteManagedStock(stockCode);
                return;
            }
            const item = target.closest('.stock-item');
            if (!item) {
                return;
            }
            const codeElement = item.querySelector('.stock-item-code');
            const code = codeElement ? codeElement.textContent.trim() : '';
            stockCodeInput.value = code;
        });
        if (adminUsersBody) {
            adminUsersBody.addEventListener('click', function(event) {
                const approveTarget = event.target.closest('.approve-user-btn');
                if (approveTarget) {
                    approveUserAccount(approveTarget.dataset.userId, approveTarget.dataset.username);
                    return;
                }
                const deleteTarget = event.target.closest('.delete-user-btn');
                if (deleteTarget) {
                    deleteUserAccount(deleteTarget.dataset.userId, deleteTarget.dataset.username);
                }
            });
        }
        themeToggleBtn.addEventListener('click', toggleTheme);

        sendReportBtn.addEventListener('click', sendReport);
        if (saveProfileBtn) {
            saveProfileBtn.addEventListener('click', saveProfileSettings);
        }
        if (profileAvatarInput) {
            profileAvatarInput.addEventListener('change', updateProfileAvatarPreview);
        }
        if (profileUsernameInput) {
            profileUsernameInput.addEventListener('keydown', function(event) {
                if (event.key === 'Enter') {
                    saveProfileSettings();
                }
            });
        }
        saveReportEmailBtn.addEventListener('click', saveReportEmailSettings);
        if (saveReportScheduleBtn) {
            saveReportScheduleBtn.addEventListener('click', saveReportScheduleSettings);
        }
        if (saveLlmPromptsBtn) {
            saveLlmPromptsBtn.addEventListener('click', saveLlmPromptSettings);
        }
        if (reportScheduleStockList) {
            reportScheduleStockList.addEventListener('change', function() {
                settingsState.reportScheduleSelectedCodes = getSelectedScheduleStockCodes();
            });
        }
        if (forumPostSubmitBtn) {
            forumPostSubmitBtn.addEventListener('click', createForumPost);
        }
        if (forumRefreshBtn) {
            forumRefreshBtn.addEventListener('click', loadForumPosts);
        }
        if (forumSortSelect) {
            forumSortSelect.addEventListener('change', function() {
                forumState.sortBy = this.value || 'created_at';
                loadForumPosts();
            });
        }
        if (forumList) {
            forumList.addEventListener('click', async function(event) {
                const likeBtn = event.target.closest('.forum-like-btn');
                if (likeBtn) {
                    await toggleForumLike(likeBtn.dataset.postId || '');
                    return;
                }
                const submitBtn = event.target.closest('.forum-comment-submit-btn');
                if (!submitBtn) {
                    return;
                }
                const postId = submitBtn.dataset.postId || '';
                const input = forumList.querySelector(`.forum-comment-input[data-post-id="${postId}"]`);
                if (!input) {
                    setForumStatus('评论输入框不存在。', 'error');
                    return;
                }
                const success = await createForumComment(postId, input.value);
                if (success) {
                    input.value = '';
                }
            });
            forumList.addEventListener('keydown', async function(event) {
                const input = event.target.closest('.forum-comment-input');
                if (!input || !(event.metaKey || event.ctrlKey) || event.key !== 'Enter') {
                    return;
                }
                event.preventDefault();
                const success = await createForumComment(input.dataset.postId || '', input.value);
                if (success) {
                    input.value = '';
                }
            });
            forumList.addEventListener('error', function(event) {
                const image = event.target.closest && event.target.closest('.forum-image img');
                if (!image) {
                    return;
                }
                const wrapper = image.closest('.forum-image');
                if (wrapper) {
                    wrapper.classList.add('forum-image-missing');
                    wrapper.textContent = `图片加载失败：${image.alt || '帖子图片'}`;
                }
            }, true);
        }
        if (forumPostContent) {
            forumPostContent.addEventListener('keydown', function(event) {
                if ((event.metaKey || event.ctrlKey) && event.key === 'Enter') {
                    createForumPost();
                }
            });
        }
        if (forumImageInput) {
            forumImageInput.addEventListener('change', updateForumImagePreview);
        }
        loadMarketSentimentBtn.addEventListener('click', loadMarketSentiment);
        loadSectorSentimentBtn.addEventListener('click', loadSectorSentiment);
        loadStockSentimentBtn.addEventListener('click', loadStockSentiment);
        if (loadAllFavoriteSentimentBtn) {
            loadAllFavoriteSentimentBtn.addEventListener('click', loadAllFavoriteStockSentiment);
        }
        sentimentSectorInput.addEventListener('change', function() {
            syncSectorSelectionByName(this.value);
        });
        sentimentFavoriteStockSelect.addEventListener('change', appendSentimentFavoriteStock);
        sentimentSectorInput.addEventListener('keydown', function(event) {
            if (event.key === 'Enter') {
                loadSectorSentiment();
            }
        });
        reportEmailInput.addEventListener('keydown', function(event) {
            if (event.key === 'Enter') {
                saveReportEmailSettings();
            }
        });
        sentimentStockCodeInput.addEventListener('keydown', function(event) {
            if (event.key === 'Enter') {
                loadStockSentiment();
            }
        });

        document.querySelectorAll('.predict-day-option:not(.market-predict-day-option)').forEach(item => {
            item.addEventListener('click', function() {
                setSelectedPredictDays(parseInt(this.getAttribute('data-days'), 10));
            });
        });
        marketPredictDayButtons.forEach(item => {
            item.addEventListener('click', function() {
                setSelectedMarketPredictDays(parseInt(this.getAttribute('data-days'), 10));
            });
        });

        if (predictCustomDaysInput) {
            predictCustomDaysInput.addEventListener('input', function() {
                const customValue = Number(this.value || 0);
                if (!customValue) {
                    return;
                }
                setSelectedPredictDays(customValue);
            });
        }
        if (marketPredictCustomDaysInput) {
            marketPredictCustomDaysInput.addEventListener('input', function() {
                const customValue = Number(this.value || 0);
                if (!customValue) {
                    return;
                }
                setSelectedMarketPredictDays(customValue);
            });
        }

        if (predictRunBtn) {
            predictRunBtn.addEventListener('click', function() {
                predictStock(selectedPredictDays);
            });
        }
        if (marketPredictRunBtn) {
            marketPredictRunBtn.addEventListener('click', function() {
                predictMarketIndex(selectedMarketPredictDays);
            });
        }
        if (predictDetailLink) {
            predictDetailLink.addEventListener('click', function() {
                switchPanel('modelInfoPanel');
            });
        }

        if (modelInfoNav) {
            modelInfoNav.addEventListener('click', function(event) {
                const navItem = event.target.closest('.model-info-nav-item');
                if (!navItem) {
                    return;
                }
                currentModelInfoIndex = Number(navItem.dataset.index || 0);
                renderModelInfoPage();
            });
        }

        initTheme();
        initAuthState().then(() => {
            if (getCurrentUserId()) {
                bootstrapAuthedData();
            }
        });
        initRiskPreference();
        initSentimentDateRanges();
        startRealtimeUiClock();
        startMarketSentimentAutoRefresh();
        renderModelInfoPage();
        setChartPeriod(365);
        setStockChartRange(365);
        stockSubmenuItems.forEach(item => {
            item.classList.toggle('active', item.dataset.stockMode === 'market');
        });
        stockSubmenu?.classList.remove('open');
        stockMenuToggle?.setAttribute('aria-expanded', 'false');
        switchForumPanel('feed');
        setSelectedPredictDays(1);
        setSelectedMarketPredictDays(1);
        setManagedStocksExpanded(false);
        startMarketAutoRefresh();
        startStockAutoRefresh();
        startRankingAutoRefresh();
        loadMarketIndices();
        loadStockRankings();
