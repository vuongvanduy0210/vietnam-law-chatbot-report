# MÔ TẢ CHI TIẾT FRONTEND

> Tổng hợp từ source code thực tế (đã verify từng file).
> Phục vụ Chương 3 (Phân tích & Thiết kế) và Chương 4 (Triển khai) của báo cáo.

---

## A. MOBILE APP — Vietnam Law Chatbot (Kotlin Multiplatform)

### A.1. Thông tin chung

- **Đường dẫn**: `d:\doan\sourcecode\vietnam-law-chatbot\Vietnam Law Chatbot\`
- **Package gốc**: `com.duyvv.lawchatbot.vietnamlawchatbot`
- **Multi-target**: `androidTarget`, `iosArm64`, `iosSimulatorArm64`, `jvm` (desktop).
- **Ngôn ngữ**: Kotlin 2.3.0.
- **UI Framework**: Compose Multiplatform 1.10.0 + Material3.
- **Số file Kotlin**: ~125 file trong `commonMain` (không tính `androidMain`/`iosMain`).

### A.2. Stack & Dependencies (xác thực từ `gradle/libs.versions.toml`)

| Mục | Thư viện | Version |
|---|---|---|
| Kotlin | `org.jetbrains.kotlin.multiplatform` | 2.3.0 |
| Compose Multiplatform | `org.jetbrains.compose` | 1.10.0 |
| Material3 | `compose.material3` | 1.10.0-alpha05 |
| Material Icons Extended | `material-icons-extended` | 1.7.3 |
| **DI** | `Koin` (BOM) | 4.1.1 |
| **HTTP Client** | `Ktor Client Core` | 3.4.0 |
| | `ktor-client-okhttp` (Android) | 3.4.0 |
| | `ktor-client-darwin` (iOS) | 3.4.2 |
| | `ktor-client-cio` (Desktop JVM) | 3.4.0 |
| | `ktor-client-auth` (Bearer + refresh) | 3.4.0 |
| | `ktor-client-logging` | 3.4.0 |
| | `ktor-client-content-negotiation` | 3.4.0 |
| **Navigation** | `androidx.navigation3:navigation3-ui` | 1.0.0-alpha06 |
| | `lifecycle-viewmodel-navigation3` | 2.10.0-alpha07 |
| **Serialization** | `kotlinx-serialization-json` | 1.10.0 |
| **DateTime** | `kotlinx-datetime` | 0.7.1 |
| **Local storage** | `androidx.datastore` + `datastore-preferences` | 1.2.0 |
| **Secure storage** | `eu.anifantakis:ksafe` + `ksafe-compose` | 1.4.2 |
| **Markdown** | `com.mikepenz:multiplatform-markdown-renderer-m3` | 0.27.0 |

> **Đặc điểm đáng chú ý**:
> - Dùng **`Navigation 3`** (alpha) — thế hệ navigation mới nhất của Compose, dựa trên `NavBackStack` + `NavEntry` thay vì `NavHost` truyền thống.
> - Dùng **KSafe** cho secure storage thay vì EncryptedSharedPreferences (cross-platform encryption).
> - **Markdown renderer** — render câu trả lời AI dạng markdown đẹp.

### A.3. Cấu trúc thư mục `commonMain/kotlin/`

```
com.duyvv.lawchatbot.vietnamlawchatbot/
├── App entry
│   ├── Platform.kt                 # expect/actual platform info
│   └── presentation/App.kt         # Composable App() entry
│
├── core/                           # MVI base infrastructure
│   ├── BaseViewModel.kt            # Generic <S, I, F> base
│   ├── MVIContract.kt              # UiState / MVIIntent / MVIEffect
│   └── cipher/CipherProvider.kt    # KSafe cipher (cho token encryption)
│
├── di/                             # Koin modules
│   ├── appModule.kt                # data + repository + viewModel modules
│   └── Koin.kt                     # init Koin (call from Android/iOS)
│
├── data/
│   ├── local/
│   │   ├── SessionManager.kt       # Singleton phát signal "session expired"
│   │   └── datastore/
│   │       ├── DataStoreManager.kt # JWT tokens, user prefs
│   │       ├── BasePreferenceManager.kt
│   │       └── createKSafe.kt      # expect/actual KSafe
│   ├── remote/
│   │   ├── Endpoint.kt             # Tất cả URL constants (xem chi tiết bên dưới)
│   │   ├── RemoteClientFactory.kt  # Ktor HttpClient + Auth + refresh
│   │   ├── RemoteUtils.kt          # safeApiCall (Result wrapper)
│   │   ├── SseClient.kt            # *** SSE streaming Flow<SseEvent> ***
│   │   ├── service/
│   │   │   ├── AuthService.kt
│   │   │   ├── ChatService.kt      # CRUD + sendMessageStream() SSE
│   │   │   ├── GuidedService.kt    # clarify + answer + answerStream() SSE
│   │   │   └── LawService.kt       # 6 endpoints (list, search, detail, AI search...)
│   │   └── dto/
│   │       ├── BaseResponse.kt
│   │       ├── request/  (10 file: ChatRequest, GuidedClarifyRequest, ...)
│   │       └── response/ (15 file: LoginResponse, MessageResponse, ChatStreamDto, GuidedResponse, ...)
│   └── repository/                 # 4 Impl: Auth, Chat, Guided, Law
│
├── domain/
│   ├── model/                      # 11 domain models
│   │   ├── ChatStreamEvent.kt      # *** Sealed: Ready / Progress / Done / Error ***
│   │   ├── PipelineStep.kt         # Pipeline step + StepStatus enum
│   │   ├── GuidedStreamEvent.kt
│   │   ├── GuidedModels.kt         # ClarifyQuestion, GuidedAnswer, ...
│   │   ├── Conversation.kt
│   │   ├── Message.kt
│   │   ├── MessageRole.kt          # USER / ASSISTANT
│   │   ├── LawDetail.kt
│   │   ├── ArticleDocument.kt
│   │   ├── AISearchResult.kt
│   │   └── LawInfo
│   ├── repository/                 # 4 interface
│   └── mapper/Mapper.kt             # DTO → Domain mappers
│
├── presentation/
│   ├── App.kt                       # Root composable
│   ├── ui/                          # Theme
│   │   ├── AppTheme.kt              # Material3 theme + AppColors
│   │   └── Type.kt                  # Typography
│   ├── component/                   # Reusable composables
│   │   ├── BaseNavDisplay.kt        # Wrapper Navigation 3 NavDisplay
│   │   ├── ThinkingPanel.kt         # *** Chain-of-thought UI animation ***
│   │   ├── TypingBubble.kt          # Streaming text bubble với cursor
│   │   ├── CreativeTextField.kt     # Custom input cho chat
│   │   └── ChatEvent.kt             # ChatStreamEvent helpers
│   ├── dialog/                      # LoadingDialog, RenameDialog
│   ├── navigation/
│   │   ├── MainRoute.kt             # Sealed interface MainRoute (10 routes)
│   │   ├── MainNavigationRoot.kt    # NavBackStack + entryProvider
│   │   └── AppNavigationActions.kt  # CompositionLocal cho navigate actions
│   └── screen/
│       ├── splash/
│       ├── login/                   # LoginContract / Screen / ViewModel
│       ├── signup/                  # Register*
│       ├── main/                    # MainViewModel (xử lý session expired)
│       └── home/
│           ├── HomeScreen.kt        # Bottom-bar 3 tabs container
│           ├── HomeContract.kt      # selectedTab state
│           ├── HomeViewModel.kt
│           ├── component/
│           │   └── CustomBottomBar.kt
│           ├── navigation/
│           │   └── HomeNavigationRoot.kt  # 3 tabs: Chat / Library / Setting
│           ├── chat/                # Tab 1: Danh sách hội thoại
│           ├── detailconversation/  # Sub-screen: cuộc hội thoại đang mở
│           ├── library/             # Tab 2: thư viện pháp luật + AI Search
│           ├── lawdetail/           # Sub-screen: chi tiết văn bản
│           ├── articledetail/       # Sub-screen: chi tiết điều luật
│           ├── guided/              # Sub-screen: Guided Consultation + SuggestedTopics
│           └── setting/             # Tab 3: cài đặt
│               ├── SettingScreen.kt
│               ├── archived/        # Hội thoại đã lưu
│               ├── changepassword/
│               └── profile/         # User profile + edit
│
└── utils/
    ├── DateTimeUtils.kt
    ├── LawTextFormatter.kt
    ├── ValidationUtils.kt
    └── Utils.kt
```

### A.4. Architecture pattern: **MVI** (Model-View-Intent)

**Contract chuẩn cho mỗi screen** (3 file):

```kotlin
// 1. ContractFile.kt
data class XxxState(...) : UiState
sealed interface XxxIntent : MVIIntent { ... }
sealed interface XxxEffect : MVIEffect { ... }

// 2. XxxViewModel.kt extends BaseViewModel<State, Intent, Effect>
//    Override createInitialState() + sendIntent()

// 3. XxxScreen.kt — Composable, collect state + send intent
```

**`BaseViewModel`** (verified từ source):

```kotlin
abstract class BaseViewModel<S : UiState, I : MVIIntent, F : MVIEffect> : ViewModel() {
    private val _uiState = MutableStateFlow(createInitialState())
    val uiState: StateFlow<S> = _uiState.asStateFlow()

    private val _effect = Channel<F>(Channel.BUFFERED)
    val effect = _effect.receiveAsFlow()

    abstract fun createInitialState(): S
    abstract fun sendIntent(intent: I)

    protected fun updateUiState(reduce: S.() -> S) { _uiState.update { it.reduce() } }
    fun sendEffect(builder: () -> F) { _effect.trySend(builder()) }

    protected val viewModelSafetyScope = viewModelScope + exceptionHandler
}
```

**Đếm screen / viewmodel** (xác nhận từ `appModule.kt`):

| # | Screen | ViewModel |
|---|---|---|
| 1 | Splash | `SplashViewModel` |
| 2 | Login | `LoginViewModel` |
| 3 | SignUp | `RegisterViewModel` |
| 4 | Home (container) | `HomeViewModel` |
| 5 | Tab Chat (list) | `ChatViewModel` |
| 6 | ChatDetail (conversation) | `ChatDetailViewModel` |
| 7 | Tab Library | `LibraryViewModel` |
| 8 | LawDetail | `LawDetailViewModel` |
| 9 | ArticleDetail | `ArticleDetailViewModel` |
| 10 | Tab Setting | `SettingViewModel` |
| 11 | ArchivedConversations | `ArchivedConversationsViewModel` |
| 12 | UserProfile | `ProfileViewModel` |
| 13 | ChangePassword | `ChangePasswordViewModel` |
| 14 | GuidedConsultation | `GuidedViewModel` |
| 15 | Main (nav root) | `MainViewModel` |

Tổng: **15 ViewModel**, ~16 màn hình chính.

### A.5. Navigation — Navigation 3

**`MainRoute`** (`navigation/MainRoute.kt`) — sealed interface, mỗi route là một `data object` hoặc `data class` được `@Serializable`:

```kotlin
@Serializable
sealed interface MainRoute : NavKey {
    @Serializable data object Splash
    @Serializable data object Login
    @Serializable data object SignUp
    @Serializable data object Home
    @Serializable data class ChatDetail(val conversationId: String)
    @Serializable data class LawDetail(val lawId: String?)
    @Serializable data class ArticleDetail(val articleId: String)
    @Serializable data object ArchivedConversations
    @Serializable data object UserProfile
    @Serializable data object ChangePassword
    @Serializable data object GuidedConsultation
}
```

**`HomeRoute`** (bottom-bar):
- `Chat` — tab "Trợ lý"
- `Library` — tab "Thư viện"
- `Setting` — tab "Cài đặt"

Tổng cộng **11 route chính** + **3 home-tab** = 14 navigation entries.

Navigation 3 dùng `rememberNavBackStack()` với `SavedStateConfiguration` để khôi phục stack sau khi process death (Android) — tương tự Navigation Compose nhưng hỗ trợ KMP tốt hơn.

### A.6. Network layer

#### A.6.1. `Endpoint.kt` — danh sách 100% các API mobile gọi

```kotlin
const val BASE_URL = "http://192.168.0.104:8000/api/v1/"  // ⚠ IP cứng — cần đổi cho production

// Auth (6)
auth/login, auth/signup, auth/logout, auth/refresh, auth/me, auth/change-password

// Chat (4)
chat/conversations
chat/messages
chat/messages/stream                          // *** SSE ***
chat/messages/{id}/suggested-questions

// Laws (7)
laws/search, laws/topics, laws/detail, laws/by-law, laws (list), laws/info
laws/ai-search                                // *** AI semantic search ***

// Guided (3)
guided/clarify
guided/answer
guided/answer/stream                          // *** SSE ***
```

> **Phát hiện quan trọng**: hệ thống có **3 endpoint streaming** (chat regular, guided answer) qua SSE, và endpoint **AI Search** trên Library — cả 2 đều là tính năng nổi bật để demo.

#### A.6.2. JWT Auth + Refresh Token Logic

**`RemoteClientFactory.createHttpClient(dataStoreManager)`** — Ktor `Auth { bearer { ... } }` plugin:

```kotlin
install(Auth) {
    bearer {
        loadTokens {
            BearerTokens(accessToken, refreshToken)  // load từ DataStore
        }
        refreshTokens {
            // Khi server trả 401:
            //  1. Gọi POST auth/refresh với refresh_token
            //  2. Lưu tokens mới vào DataStore
            //  3. Trả BearerTokens mới — Ktor tự động retry request bị 401
            //  4. Nếu refresh fail → SessionManager.notifySessionExpired() → MainViewModel.effect → MainNavigationRoot redirect Login
        }
    }
}
```

**Đặc điểm**:
- Token tự động đính kèm vào mọi request (header `Authorization: Bearer ...`).
- Refresh **hoàn toàn tự động** — UI không cần handle 401.
- Nếu refresh fail → `SessionManager.notifySessionExpired()` phát signal → đẩy về Login.

#### A.6.3. SSE Streaming — `SseClient.kt` (verified)

```kotlin
inline fun <reified T : Any> streamSse(
    client: HttpClient,
    endpoint: String,
    body: T,
): Flow<SseEvent> = callbackFlow {
    client.preparePost(endpoint) {
        setBody(body)
        accept(ContentType("text", "event-stream"))
        timeout {
            requestTimeoutMillis = 600_000
            socketTimeoutMillis = 600_000
        }
    }.execute { response ->
        val channel = response.bodyAsChannel()
        var event = "message"
        val dataBuf = StringBuilder()

        while (!channel.isClosedForRead) {
            val line = channel.readUTF8Line() ?: break
            when {
                line.isEmpty() -> { /* flush 1 frame */ trySend(SseEvent(event, dataBuf.toString())) }
                line.startsWith(":") -> { /* heartbeat — bỏ qua */ }
                line.startsWith("event:") -> { event = line.substring(6).trim() }
                line.startsWith("data:") -> { dataBuf.append(line.substring(5).trimStart()) }
            }
        }
    }
}
```

> **Comment trong code (rất giá trị viết báo cáo)**:
> *"Dùng `callbackFlow` (channel-based) thay `flow { }` vì Ktor's `execute { }` tạo `UndispatchedCoroutine` con — emit từ context đó vào `flow { }` builder sẽ throw 'Flow invariant violated'."*

→ Đây là **chi tiết kỹ thuật rất sâu** đáng đưa vào báo cáo: thể hiện hiểu sâu về Coroutines + Flow.

#### A.6.4. ChatStreamEvent (Domain layer)

```kotlin
sealed interface ChatStreamEvent {
    data class Ready(conversationId, isNewConversation, userMessage) : ChatStreamEvent
    data class Progress(steps: List<PipelineStep>) : ChatStreamEvent
    data class Done(conversationId, isNewConversation, assistantMessage, suggestedQuestions) : ChatStreamEvent
    data class Error(message: String) : ChatStreamEvent
}

data class PipelineStep(id, label, status: PENDING | RUNNING | DONE, subSteps)
```

Repository `ChatRepositoryImpl.sendMessageStream()` map từ raw `SseEvent.event` (ready / progress / done / error) → `ChatStreamEvent` domain → emit vào `Flow`.

### A.7. UI components độc đáo

| Component | File | Mô tả |
|---|---|---|
| **ThinkingPanel** | `presentation/component/ThinkingPanel.kt` | Vertical timeline + animated status badges hiển thị 5 bước pipeline RAG đang chạy (Guardrail → Query Analysis → Agent → Tools → Verifier). Auto-collapse khi xong, click để expand lại. |
| **TypingBubble** | `presentation/component/TypingBubble.kt` | Bubble streaming text với hiệu ứng typing cursor. |
| **CreativeTextField** | `presentation/component/CreativeTextField.kt` | Custom multiline input cho chat với placeholder gradient. |
| **CustomBottomBar** | Bottom navigation 3 tab có hiệu ứng selected. |
| **BaseNavDisplay** | Wrapper `androidx.navigation3.ui.NavDisplay` cho consistency. |

**Markdown rendering**: dùng `multiplatform-markdown-renderer-m3` để render câu trả lời AI (chứa `**bold**`, list, citation links).

### A.8. Local storage

- **`DataStoreManager`** — sử dụng `androidx.datastore.preferences` (KMP-compatible từ AndroidX 1.2):
  - `accessToken` (String)
  - `refreshToken` (String)
  - `userId`, user preferences khác.
- **`KSafe`** — encrypted storage cho thông tin nhạy cảm (cipher provided qua `CipherProvider`).
- **Không có SQLDelight / Room / Realm** — tất cả data fetch từ server, không cache offline.

### A.9. Platform-specific code

**`androidMain`**:
- `MainActivity.kt` — Activity duy nhất, gọi `setContent { App() }`.
- `Platform.android.kt` — actual implementation cho expect interface.
- `KoinAndroid.kt` — init Koin với Android context.
- `createKSafe.android.kt` — actual KSafe cipher dùng Android KeyStore.

**`iosMain`**:
- Tương tự, expect/actual cho Platform info, KSafe (dùng iOS Keychain).
- `iosApp/iOSApp.swift` — entry point SwiftUI gọi `ComposeApp.framework`.

**`jvmMain`** (desktop):
- Có thể chạy như desktop app (Windows/Mac/Linux) — nhưng phục vụ chính là Android + iOS.

### A.10. Localization & Theme

- Tất cả text **tiếng Việt** hardcoded — không dùng resources string (chấp nhận được vì đồ án 1 ngôn ngữ).
- `AppTheme` + `AppColors` Material3 theme.
- Theme branding chính: gradient `#00BFA5` (teal) ↔ `#6378FF` (indigo) — đồng bộ với web admin.

### A.11. Test code

- `commonTest/` — tồn tại nhưng chỉ có `kotlin.test` plugin được declare; chưa thấy test cases thực sự đáng kể.
- **Chưa có UI test** (Espresso / Compose UI Test).
- → Trong phần "Hạn chế" của báo cáo có thể nêu: chưa hoàn thiện unit + UI test.

---

## B. WEB ADMIN — Vietnam Law Admin (Next.js)

### B.1. Thông tin chung

- **Đường dẫn**: `d:\doan\sourcecode\vietnam-law-admin-fe\`
- **Framework**: **Next.js 16.1.6** (App Router) với **React 19.2.3**.
- **Ngôn ngữ**: TypeScript 5.x (strict mode).
- **Styling**: **TailwindCSS 4.x** + `tw-animate-css`.
- **UI Library**: **shadcn/ui 3.8.5** (built on Radix UI 1.4.3).

### B.2. Stack & Dependencies (xác thực từ `package.json`)

| Mục | Package | Version |
|---|---|---|
| Framework | `next` | 16.1.6 |
| React | `react`, `react-dom` | 19.2.3 |
| Styling | `tailwindcss` | 4.x |
| UI primitives | `radix-ui` | 1.4.3 |
| UI builder | `shadcn` | 3.8.5 |
| Icons | `lucide-react` | 0.575.0 |
| Forms | `react-hook-form` + `@hookform/resolvers` + `zod` | 7.71 / 5.2 / 4.3 |
| HTTP | `axios` | 1.13.5 |
| Storage | `js-cookie` | 3.0.5 |
| Charts | `recharts` | 3.7.0 |
| Toast | `sonner` | 2.0.7 |
| Date | `date-fns` | 4.1.0 |
| Utils | `clsx`, `tailwind-merge`, `class-variance-authority` |

### B.3. Cấu trúc thư mục

```
vietnam-law-admin-fe/
├── public/                 # Static assets
├── src/
│   ├── app/                # Next.js App Router (file-based routing)
│   │   ├── layout.tsx      # Root layout (Toaster, fonts)
│   │   ├── page.tsx        # /  → Login page (~220 dòng)
│   │   └── dashboard/
│   │       ├── layout.tsx          # Auth check + Sidebar + Header + WS provider
│   │       ├── page.tsx            # Dashboard tổng quan (stats, biểu đồ)
│   │       ├── documents/
│   │       │   ├── page.tsx        # Danh sách văn bản
│   │       │   ├── upload/page.tsx # Upload PDF + tracking
│   │       │   └── tasks/          # (rỗng — có thể đã merge sang tracker)
│   │       ├── tracker/page.tsx    # Theo dõi document tasks
│   │       └── library/            # (rỗng / đang phát triển)
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Sidebar.tsx         # 3 nav items
│   │   │   └── Header.tsx          # User dropdown
│   │   └── ui/                     # 14 shadcn components: avatar, badge, button, card,
│   │                               # dialog, dropdown-menu, form, input, label, progress,
│   │                               # scroll-area, separator, sheet, table
│   ├── lib/
│   │   ├── apiClient.ts            # axios instance + interceptors
│   │   └── utils.ts                # cn() helper
│   └── providers/
│       └── WebSocketProvider.tsx   # *** Realtime task tracking ***
├── package.json
├── tsconfig.json
├── next.config.ts
├── eslint.config.mjs
├── postcss.config.mjs              # Tailwind 4 plugin
├── components.json                 # shadcn config
└── Dockerfile                      # Production build
```

### B.4. Các trang chính (verified từ App Router)

#### B.4.1. Login Page (`/`)

- **File**: `src/app/page.tsx` (220 dòng).
- **Chức năng**:
  - Form email/password (custom Tailwind, không dùng react-hook-form ở đây).
  - Gọi `POST /auth/login` qua axios trực tiếp (không qua apiClient).
  - **Verify role admin** sau login: gọi `GET /auth/me`, từ chối nếu `role !== "admin"`.
  - Lưu token vào cookie `admin_token` (expires 1 day, sameSite=strict, secure tự động bật khi HTTPS).
  - **Mapping error code → tiếng Việt**: `AUTH_1001` → "Email/mật khẩu không chính xác", v.v. (8 mã AUTH + 3 VALIDATION + 3 RESOURCE + 3 NETWORK).
  - Redirect `/dashboard` khi thành công.
  - Auto-redirect khi đã có token.
- **UI**: 2-column layout (left: branding teal-indigo gradient, right: form).

#### B.4.2. Dashboard Layout (`/dashboard/layout.tsx`)

- **Auth guard**: check token cookie + role admin → redirect `/` nếu không hợp lệ.
- Hiển thị: `<Sidebar />` + `<Header user />` + `<WebSocketProvider>` wrap toàn bộ children.
- Loading state khi đang verify.

#### B.4.3. Dashboard Overview (`/dashboard/page.tsx`)

- **API**: `GET /dashboard/stats`.
- **Stats hiển thị**:
  - Total laws, total articles, success_count, failed_count, processing_count.
  - Top topics (mảng `{topic, count}`).
  - Latest tasks (mảng task gần nhất).
- **Realtime**: tích hợp `useWebSocket()` — khi 1 task hoàn thành, auto-refetch stats.
- **Biểu đồ**: `BarChart` từ `recharts` cho top topics.

#### B.4.4. Document List (`/dashboard/documents`)

- **API**: `GET /laws` (paginated 15/page), `GET /laws/info?law_id=...`, `GET /laws/detail?id=...`.
- **Features**:
  - Search (debounce input).
  - Pagination với prev/next.
  - **Detail modal**: click vào law → mở Dialog với danh sách articles → click article → expand lazy load article detail.
  - Status badge: completed / failed / processing với màu sắc.
  - Refresh button + RefreshCcw icon.

#### B.4.5. Upload Document (`/dashboard/documents/upload`)

- **API**: `POST /documents/upload` (multipart with file).
- **Features chính**:
  - **Drag & drop** file upload (PDF, max 100MB).
  - **AbortController** để cancel upload đang chạy.
  - Phase state machine: `idle → uploading → processing → done | error`.
  - **Resume task**: nếu reload page giữa upload, dùng `task_id` lưu localStorage → `GET /documents/tasks/{id}` để khôi phục state.
  - **Realtime progress** qua WebSocket (subscribe `UPLOAD_PROGRESS` event).
  - Hiển thị từng article đã parse: `articleId`, `title`, `text`, metadata (topics, keywords, summary).
  - Expand/collapse mỗi article.

#### B.4.6. Tracker Page (`/dashboard/tracker`)

- **API**: `GET /documents/tasks`.
- Bảng tất cả document tasks: filename, status, progress, current_step, law_id, article_count, created_at, completed_at.
- Merge realtime updates từ WebSocket vào bảng.
- Auto-connect WS khi có task đang processing.

### B.5. WebSocket Provider (`providers/WebSocketProvider.tsx`)

> Đây là **điểm sáng kỹ thuật** trên web admin — tương đương SSE trên mobile.

```typescript
// Endpoint: ws://localhost:8000/api/v1/documents/ws?token=...
// (Token qua query param vì browser WebSocket API không cho set Authorization header)

interface TaskUpdate {
    task_id, status, progress, current_step, error,
    filename, law_id, article_count
}

// Provider expose:
{
  activeTasks: Record<task_id, TaskUpdate>,
  connectToTracker: () => void,
  disconnectTracker: () => void
}
```

**Đặc điểm**:
- **Auto-connect** khi có task đang processing.
- **Auto-disconnect** khi tất cả tasks đã xong.
- **Auto-reconnect** với retry limit 3 lần (3s delay).
- Phân biệt 2 message types từ server:
  - `UPLOAD_PROGRESS` — chỉ cập nhật progress số.
  - `UPLOAD_STATUS` — cập nhật status + show toast (`toast.success/error/info`).
- Cleanup đúng cách khi unmount để tránh memory leak.

### B.6. API Client (`lib/apiClient.ts`)

```typescript
const apiClient = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1",
    headers: { "Content-Type": "application/json" },
});

// Request interceptor: tự động gắn Bearer token từ cookie
// Response interceptor:
//  - 401 → xóa cookie + redirect "/" (nếu đang ở /dashboard)
//  - 403 → tương tự (không có quyền admin)
```

> **Không có refresh token tự động** trên web (khác với mobile dùng Ktor `Auth` plugin) — web đơn giản: token hết hạn → đăng nhập lại. Có thể nêu trong "Hướng phát triển".

### B.7. Sidebar Navigation

3 nav items:
1. **Tổng quan** — `/dashboard` (icon: LayoutDashboard).
2. **Quản lý Văn bản** — `/dashboard/documents` (icon: FileText).
3. **Tiến trình Xử lý (RAG)** — `/dashboard/tracker` (icon: Activity).

Logo: Scale icon + "VN Law Admin".

### B.8. UI Design System

- **Branding colors**: gradient `#00BFA5` (teal) → `#6378FF` (indigo) — đồng bộ với mobile app.
- **Selection color**: `bg-teal-500/30` (highlight teal).
- **Dark mode**: support sẵn qua `dark:` Tailwind classes.
- **Shadcn components**: 14 components reusable.
- **Toast**: `sonner` library.
- **Charts**: `recharts` (ResponsiveContainer + BarChart).
- **Animations**: `tw-animate-css` (animate-in fade-in slide-in-from-bottom-4).

### B.9. Phương thức xác thực

| Phía | Cơ chế |
|---|---|
| **Login → Cookie** | `Cookies.set("admin_token", access_token, { expires: 1, sameSite: "strict", secure })` |
| **Mỗi request** | axios interceptor gắn `Authorization: Bearer <token>` |
| **WebSocket** | Token qua query param vì browser WS API không cho header tùy chỉnh |
| **Server-side check** | `/dashboard` layout verify `auth/me` mỗi lần mount, role phải = "admin" |

### B.10. Đặc điểm cần highlight cho báo cáo

1. **Realtime updates qua WebSocket** — task tracking, dashboard stats refetch tự động khi có task xong.
2. **Resume upload sau reload tab** — dùng localStorage để khôi phục task_id + REST `GET /tasks/{id}` để build lại UI state.
3. **AbortController** — cho phép cancel upload đang chạy.
4. **Type safety end-to-end** — TypeScript interfaces cho mọi DTO.
5. **shadcn/ui + TailwindCSS 4** — modern stack 2025.
6. **Error code mapping** — 17 mã lỗi backend được map sang tiếng Việt.
7. **Auth guard** — middleware check role admin mọi route /dashboard.

---

## C. SO SÁNH MOBILE vs ADMIN — bố cục Chương 3

| Khía cạnh | Mobile (KMP) | Admin (Next.js) |
|---|---|---|
| Đối tượng người dùng | Người dùng cuối (sinh viên, người dân, cán bộ pháp chế) | Quản trị viên hệ thống |
| Tính năng chính | Chat AI, Library tra cứu, Guided Consultation, AI Search | Upload PDF, theo dõi pipeline, dashboard thống kê |
| Realtime tech | **SSE** (Ktor + Flow) | **WebSocket** (browser native API) |
| Auth refresh | **Tự động** qua Ktor `Auth { bearer { refreshTokens } }` | Manual login khi 401 |
| State management | **MVI** (BaseViewModel<S, I, F> + StateFlow + Channel) | React hooks (useState, useContext, useEffect) |
| Navigation | **Navigation 3** (alpha, KMP-native) | Next.js App Router (file-based) |
| DI | Koin | None (singleton apiClient) |
| Form validation | Tự viết (ValidationUtils) | react-hook-form + zod |
| Styling | Compose Material3 | TailwindCSS 4 + shadcn/ui |
| Markdown render | `multiplatform-markdown-renderer-m3` | (Chưa cần — chỉ hiển thị plain text) |
| Charts | Không | recharts (BarChart) |

---

## D. ĐIỂM KỸ THUẬT NỔI BẬT NÊN VIẾT VÀO BÁO CÁO

### D.1. Mobile (KMP)

1. **Kotlin Multiplatform với Compose Multiplatform** — chia sẻ ~95% code giữa Android và iOS, đúng chuyên ngành "Phát triển phần mềm di động".
2. **MVI architecture với BaseViewModel<S, I, F>** — separation of concerns rõ ràng giữa State / Intent / Effect.
3. **SSE streaming custom implementation** — Ktor không có SSE plugin chính thức cho KMP, code tự build với `callbackFlow` để vượt qua "Flow invariant violated" của Ktor's `UndispatchedCoroutine`.
4. **Pipeline thinking panel** — animate hiển thị 5 bước RAG đang chạy, nâng cao UX rõ rệt.
5. **JWT auto-refresh qua Ktor Auth plugin** — production-grade authentication.
6. **Navigation 3** — thế hệ navigation mới của Compose, hỗ trợ KMP tốt hơn Navigation Compose 2.x.
7. **Type-safe DTO ↔ Domain mapper** — sealed classes cho ChatStreamEvent, GuidedStreamEvent, MessageRole.

### D.2. Admin (Next.js)

1. **WebSocket realtime tracking** — task progress + status updates đến UI realtime.
2. **Resume upload state sau reload** — kết hợp localStorage + REST API lưu/khôi phục.
3. **Auto-reconnect WS với retry limit** — production-grade error handling.
4. **Role-based access control** — verify admin role 2 lần (login + layout).
5. **Realtime dashboard** — auto-refetch stats khi có task xong.
6. **Type-safe error mapping** — 17 mã lỗi backend → tiếng Việt.
7. **Modern stack 2025** — Next.js 16, React 19, TailwindCSS 4, shadcn/ui 3.8.

---

## E. TÍNH NĂNG ĐÃ TRIỂN KHAI (verified — không phải dự đoán)

> Cập nhật so với plan v1 — sau khi đọc code thực tế.

| Tính năng | Backend | Mobile | Web Admin | Trạng thái |
|---|---|---|---|---|
| Đăng ký / Đăng nhập | ✅ | ✅ | ✅ | DONE |
| JWT + Refresh tokens | ✅ | ✅ tự động | ⚠ chỉ login | DONE (mobile auto, web manual) |
| Quản lý hội thoại (CRUD, pin, archive) | ✅ | ✅ | — | DONE |
| Chat AI Agentic RAG | ✅ | ✅ | — | DONE |
| **Chat streaming SSE** | ✅ `/chat/messages/stream` | ✅ `sendMessageStream` | — | **DONE** |
| **Pipeline thinking panel** | ✅ progress events | ✅ ThinkingPanel composable | — | **DONE** |
| **Suggested Questions** | ✅ `/messages/{id}/suggested-questions` | ✅ | — | **DONE** |
| Guided Consultation Clarify | ✅ `/guided/clarify` | ✅ | — | DONE |
| Guided Consultation Answer (sync) | ✅ `/guided/answer` | ✅ | — | DONE |
| **Guided Answer streaming SSE** | ✅ `/guided/answer/stream` | ✅ `answerStream` | — | **DONE** |
| Library — list/search/filter | ✅ | ✅ | ✅ | DONE |
| Library — Law detail / Article detail | ✅ | ✅ | ✅ | DONE |
| **AI-Powered Search** | ✅ `POST /laws/ai-search` | ✅ `aiSearch` (LawService) | — | **DONE** |
| Cài đặt (Profile, ChangePassword) | ✅ | ✅ | — | DONE |
| Archived conversations view | ✅ | ✅ | — | DONE |
| Upload PDF | ✅ | — | ✅ | DONE |
| **WebSocket task tracking** | ✅ `/documents/ws` | — | ✅ WebSocketProvider | **DONE** |
| Document list (admin) | ✅ | — | ✅ | DONE |
| Tracker page (history tasks) | ✅ | — | ✅ | DONE |
| Dashboard stats | ✅ `/dashboard/stats` | — | ✅ | DONE |
| Bookmark điều luật | ❌ | ❌ | ❌ | NOT DONE |
| Feedback / Rating AI | ❌ | ❌ | ❌ | NOT DONE |
| Share điều luật | ❌ | ❌ | ❌ | NOT DONE |
| Lịch sử tra cứu | ❌ | ❌ | ❌ | NOT DONE |
| Quản lý người dùng (admin) | ⚠ | — | ❌ | Backend có, web chưa làm UI |

> **PHÁT HIỆN QUAN TRỌNG**: Suggested Questions, Streaming Response (chat thường), AI-Powered Search **đã hoàn thành** — khác với suy đoán ban đầu trong memory cũ. Đây là các tính năng "wow" lớn nhất, cần đẩy mạnh trong báo cáo.
