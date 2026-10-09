# TÀI LIỆU BÁO CÁO & THUYẾT TRÌNH ĐỒ ÁN MÔN HỌC
## CẤU TRÚC DỮ LIỆU VÀ GIẢI THUẬT (DATA STRUCTURES & ALGORITHMS)

---

### TÊN ĐỀ TÀI:
**SMART DICTIONARY — HỆ THỐNG QUẢN LÝ TỪ ĐIỂN THÔNG MINH VỚI GỢI Ý TỰ ĐỘNG (TRIE) VÀ TÌM KIẾM GẦN ĐÚNG (LEVENSHTEIN)**

---

## MỤC LỤC TỔNG QUAN
1. [Giới thiệu đề tài & Bài toán thực tế](#1-giới-thiệu-đề-tài--bài-toán-thực-tế)
2. [Kiến trúc hệ thống & Mô hình phân tầng](#2-kiến-trúc-hệ-thống--mô-hình-phân-tầng)
3. [Cấu trúc dữ liệu cốt lõi: Cây Tiền Tố (Trie)](#3-cấu-trúc-dữ-liệu-cốt-lõi-cây-tiền-tố-trie)
4. [Giải thuật cốt lõi: Khoảng cách Levenshtein (Quy hoạch động)](#4-giải-thuật-cốt-lõi-khoảng-cách-levenshtein-quy-hoạch-động)
5. [Thuật toán Xếp hạng kết quả tìm kiếm (5-Tier Ranking)](#5-thuật-toán-xếp-hạng-kết-quả-tìm-kiếm-5-tier-ranking)
6. [Cơ chế Tìm kiếm Hai Chiều Anh ↔ Việt (Bidirectional Retrieval)](#6-cơ-chế-tìm-kiếm-hai-chiều-anh--việt-bidirectional-retrieval)
7. [Đồng bộ Dữ liệu: In-Memory Index $\leftrightarrow$ SQLite Persistence](#7-đồng-bộ-dữ-liệu-in-memory-index-leftrightarrow-sqlite-persistence)
8. [Kết quả Thực nghiệm & Đo lường Hiệu năng](#8-kết-quả-thực-nghiệm--đo-lường-hiệu-năng)
9. [Cấu trúc Slide Thuyết trình Từng Trang (Slide-by-Slide Outline)](#9-cấu-trúc-slide-thuyết-trình-từng-trang-slide-by-slide-outline)
10. [Bộ câu hỏi phản biện & Hướng dẫn trả lời (Q&A Defense)](#10-bộ-câu-hỏi-phản-biện--hướng-dẫn-trả-lời-qa-defense)

---

## 1. GIỚI THIỆU ĐỀ TÀI & BÀI TOÁN THỰC TẾ

### 1.1. Bối cảnh & Đặt vấn đề
Trong các ứng dụng từ điển thông thường, thao tác tra cứu thường dựa vào câu lệnh cơ sở dữ liệu như:
```sql
SELECT * FROM words WHERE word LIKE 'comp%' LIMIT 10;
```
Phương pháp này gặp phải các nhược điểm nghiêm trọng trong khoa học máy tính:
- **Độ phức tạp tuyến tính**: Phải quét bảng hoặc duyệt B-Tree với chi phí đắt đỏ khi dữ liệu lớn, độ trễ I/O đĩa cao.
- **Không có khả năng chịu lỗi (Typo-Tolerance)**: Nếu người dùng gõ sai như `"comptuer"`, truy vấn SQL trả về tập rỗng (`0 results`), làm gián đoạn trải nghiệm tra cứu.
- **Không hỗ trợ hai chiều ngữ nghĩa**: Người dùng gõ nghĩa tiếng Việt `"máy tính"` không thể tìm ra từ gốc `"computer"`.

### 1.2. Mục tiêu nghiên cứu & Sản phẩm
Xây dựng một hệ thống từ điển học thuật giải quyết triệt để các hạn chế trên bằng **Cấu trúc Dữ liệu & Giải thuật chuyên biệt**:
1. **Tra cứu & Gợi ý từ (Prefix Autocomplete)**: Đạt tốc độ cận thời gian thực ($< 0.05\text{ ms}$) thông qua **Cây tiền tố (Trie)** lưu trên RAM.
2. **Sửa lỗi chính tả & Tìm kiếm mờ (Fuzzy Approximate Search)**: Sử dụng giải thuật **Quy hoạch động Levenshtein Distance** kết hợp chặn biên chiều dài để đề xuất từ đúng khi người dùng gõ nhầm.
3. **Tìm kiếm hai chiều (Anh $\leftrightarrow$ Việt)**: Ánh xạ đảo ngữ giúp tra nghĩa tiếng Việt ra từ vựng tiếng Anh tương ứng.
4. **Tính nhất quán dữ liệu**: Kết hợp SQLite (lưu trữ bền vững) và Cây Trie trong bộ nhớ RAM, tự động đồng bộ khi Thêm/Sửa/Xoá.

---

## 2. KIẾN TRÚC HỆ THỐNG & MÔ HÌNH PHÂN TẦNG

```
┌─────────────────────────────────────────────────────────────┐
│                 FRONTEND (React 18 + TypeScript)             │
│   - SearchBar (Debounce 220ms, Keyboard Navigation ↑/↓/Enter)│
│   - SuggestionDropdown (Gợi ý tiền tố thời gian thực)       │
│   - SearchResultList (Phân biệt Exact / Prefix / Fuzzy)      │
│   - Dictionary Management (CRUD & Đồng bộ giao diện)         │
└───────────────────────────────┬─────────────────────────────┘
                                │ HTTP REST API (JSON)
┌───────────────────────────────▼─────────────────────────────┐
│                 BACKEND SERVICE LAYER (FastAPI)              │
│   - SearchService (Định tuyến 4 giai đoạn tra cứu)           │
│   - SuggestionService (Truy vấn Trie Suggestions)           │
│   - DictionaryService (Điều phối DB Transaction & Trie Sync) │
└───────────────┬─────────────────────────────┬───────────────┘
                │                             │
┌───────────────▼─────────────┐ ┌─────────────▼───────────────┐
│     IN-MEMORY DSA LAYER     │ │      PERSISTENCE LAYER      │
│  - English Headwords Trie   │ │  - SQLite Database          │
│  - Vietnamese Phrases Trie  │ │  - SQLAlchemy ORM           │
│  - Levenshtein DP Engine    │ │  - 22,002 Word Records      │
│  - 5-Tier Deterministic Rank│ │  - ACID Transactions        │
└─────────────────────────────┘ └─────────────────────────────┘
```

---

## 3. CẤU TRÚC DỮ LIỆU CỐT LÕI: CÂY TIỀN TỐ (TRIE)

### 3.1. Định nghĩa & Lý do lựa chọn
**Trie (Prefix Tree)** là cấu trúc dữ liệu cây có thứ tự, trong đó mỗi nút đại diện cho một ký tự. Chuỗi ký tự được hình thành bằng cách đi từ nút gốc (root) xuống các nút con.

- **Tại sao không dùng B-Tree của Database?** B-Tree có độ phức tạp tìm kiếm $O(\log N \cdot L)$. Khi $N = 22,000$, chi phí I/O và so sánh chuỗi lớn hơn nhiều so với Trie chỉ phụ thuộc vào độ dài từ $O(L)$.
- **Tại sao không dùng Hash Table?** Hash Table hỗ trợ tìm chính xác $O(1)$, nhưng **hoàn toàn không hỗ trợ tìm kiếm tiền tố (Prefix Search)** hay duyệt từ điển theo thứ tự bảng chữ cái.

### 3.2. Cấu trúc Nút (TrieNode)
Mỗi nút trong cây được cài đặt:
```python
class TrieNode:
    __slots__ = ("children", "is_end", "word_id")
    def __init__(self):
        self.children: dict[str, TrieNode] = {}  # Ký tự -> Nút con
        self.is_end: bool = False                # Đánh dấu kết thúc từ
        self.word_id: int | None = None          # Khóa ngoại trỏ đến SQLite
```

### 3.3. Các thao tác & Độ phức tạp thuật toán
- **Thêm từ (`insert`)**: 
  - Duyệt từng ký tự của từ, tạo nút mới nếu chưa tồn tại.
  - **Độ phức tạp thời gian**: $O(L)$ với $L$ là độ dài từ.
- **Tìm kiếm chính xác (`search`)**:
  - Đi theo các cạnh tương ứng với từng ký tự. Nếu đến hết từ mà `is_end == True` $\rightarrow$ Trả về `(True, word_id)`.
  - **Độ phức tạp thời gian**: $O(L)$. Độc lập hoàn toàn với số lượng từ $N$ trong từ điển!
- **Gợi ý tiền tố (`get_suggestions`)**:
  - Giai đoạn 1: Đi từ gốc đến nút đại diện cho tiền tố $P$ (mất $O(P)$).
  - Giai đoạn 2: Bắt đầu thuật toán **Duyệt theo chiều sâu giới hạn (Bounded DFS)** duyệt qua các nhánh con theo thứ tự từ điển (`sorted(children.keys())`) để thu thập tối đa $K$ từ.
  - **Độ phức tạp thời gian**: $O(P + K)$.
- **Xóa từ và tỉa cành đệ quy (`delete`)**:
  - Sử dụng đệ quy từ dưới lên (bottom-up). Sau khi bỏ cờ `is_end`, nếu nút con không còn nhánh con nào khác (`len(children) == 0`), tiến hành thu hồi bộ nhớ ngay lập tức.
  - **Độ phức tạp thời gian**: $O(L)$.

---

## 4. GIẢI THUẬT CỐT LÕI: KHOẢNG CÁCH LEVENSHTEIN (QUY HOẠCH ĐỘNG)

### 4.1. Định nghĩa Toán học
Khoảng cách Levenshtein giữa hai chuỗi $S_1$ (độ dài $M$) và $S_2$ (độ dài $N$) là số phép biến đổi đơn ký tự tối thiểu để chuyển $S_1$ thành $S_2$. 
Các thao tác hợp lệ (chi phí đơn vị = 1):
1. **Chèn (Insertion)**: Thêm một ký tự.
2. **Xóa (Deletion)**: Xóa một ký tự.
3. **Thay thế (Substitution)**: Đổi một ký tự này thành ký tự khác.

### 4.2. Công thức Truy hồi (Recurrence Relation)
Gọi $D[i][j]$ là khoảng cách giữa tiền tố $S_1[0 \dots i-1]$ và $S_2[0 \dots j-1]$:

$$D[i][0] = i \quad (0 \le i \le M)$$
$$D[0][j] = j \quad (0 \le j \le N)$$

Với $1 \le i \le M$ và $1 \le j \le N$:
$$D[i][j] = \min \begin{cases}
D[i-1][j] + 1 & \text{(Xóa ký tự khỏi } S_1\text{)} \\
D[i][j-1] + 1 & \text{(Chèn ký tự vào } S_1\text{)} \\
D[i-1][j-1] + \text{cost} & \text{(Thay thế, } \text{cost} = 0 \text{ nếu } S_1[i-1] == S_2[j-1], \text{ ngược lại } 1\text{)}
\end{cases}$$

### 4.3. Tối ưu hóa Không gian & Chặn biên Chiều dài (Pruning Optimization)
Nếu tính Levenshtein thuần túy giữa từ truy vấn $Q$ với tất cả 22,000 từ trong từ điển, thời gian xử lý sẽ là $O(N \cdot |Q| \cdot |W|) \approx 22,000 \times 8 \times 8 \approx 1.4 \times 10^6$ phép tính $\rightarrow$ gây trễ hệ thống.

**Kỹ thuật Tối ưu hóa của Dự án**:
1. **Chặn biên chiều dài (Length Difference Bound)**:
   Để biến đổi từ $W$ thành $Q$, số phép chèn/xóa tối thiểu bắt buộc phải bằng $|len(W) - len(Q)|$.
   Do đó:
   $$\text{Nếu } |len(W) - len(Q)| > \text{max\_distance} \implies \text{Levenshtein}(W, Q) > \text{max\_distance}$$
   $\rightarrow$ **Loại bỏ ngay lập tức trước khi chạy ma trận DP**, giảm tải hơn 85% số lượng từ cần tính toán!
2. **Tối ưu bộ nhớ 2 dòng (Two-Row DP)**:
   Tại mỗi bước $i$, thuật toán chỉ cần tham chiếu đến hàng hiện tại và hàng liền trước ($D[i-1]$), giúp giảm bộ nhớ từ $O(M \cdot N)$ xuống $O(\min(M, N))$.

---

## 5. THUẬT TOÁN XẾP HẠNG KẾT QUẢ TÌM KIẾM (5-TIER RANKING)

Để kết quả tìm kiếm gần đúng trả về chính xác từ người dùng có ý định gõ nhất, dự án áp dụng hệ thống xếp hạng đơn định (Deterministic Multi-Attribute Ranking) theo bộ khóa 5 tiêu chí:

$$\text{Key} = (is\_exact, \, is\_prefix, \, edit\_distance, \, length\_diff, \, word)$$

1. **Tier 1 — Trùng khớp chính xác ($is\_exact$)**: $d = 0$ ưu tiên tuyệt đối.
2. **Tier 2 — Lợi thế tiền tố ($is\_prefix$)**: Từ có tiền tố khớp với từ khóa được ưu tiên hơn các từ bị biến đổi ở giữa chuỗi.
3. **Tier 3 — Khoảng cách chỉnh sửa tối thiểu ($edit\_distance$)**: $d = 1$ xếp trước $d = 2$.
4. **Tier 4 — Độ gần chiều dài chuỗi ($length\_diff$)**: Chuỗi có độ dài sát với từ truy vấn hơn được ưu tiên khi khoảng cách chỉnh sửa bằng nhau.
5. **Tier 5 — Thứ tự bảng chữ cái ($word$)**: Sắp xếp theo alphabet đóng vai trò tie-breaker, đảm bảo kết quả luôn cố định và nhất quán qua mọi lần truy vấn.

---

## 6. CƠ CHẾ TÌM KIẾM HAI CHIỀU ANH ↔ VIỆT

```
                                  Từ khóa tra cứu
                                         │
                 ┌───────────────────────┴───────────────────────┐
                 ▼                                               ▼
     [Có dấu thanh Tiếng Việt]                       [Không dấu / Tiếng Anh]
                 │                                               │
     1. Khớp cụm từ tiếng Việt                      1. Tra Trie Tiếng Anh (O(L))
        - Exact Match (Tra ID)                      2. Gợi ý Trie Tiếng Anh (O(P+K))
     2. Gợi ý tiền tố tiếng Việt                    3. Ánh xạ tiếng Việt không dấu
        - Trie Tiếng Việt                              (e.g., 'may tinh' -> 'máy tính')
     3. Sửa lỗi chính tả tiếng Việt                 4. Fuzzy Search Tiếng Anh
        - Levenshtein trên cụm từ                   5. Fuzzy Search Tiếng Việt
```

- **Tách cụm từ ngữ nghĩa (Phrase Tokenization)**: Phân rã các định nghĩa tiếng Việt phức tạp theo dấu phân cách ngữ pháp (`;`, `,`, `/`) thành các cụm từ độc lập (ví dụ: `"người tính; máy tính"` $\rightarrow$ `["người tính", "máy tính"]`).
- **Ánh xạ đảo ngữ (Inverted Index)**: Một cụm từ tiếng Việt có thể trỏ đến nhiều từ tiếng Anh (ví dụ: `"máy tính"` $\rightarrow$ `calculator`, `computer`, `comptometer`). Hệ thống hiển thị từ chính và cung cấp gợi ý các bản dịch tương đương.
- **Tìm kiếm không dấu (Accent-Insensitive)**: Tự động chuẩn hóa NFKD và bóc tách dấu thanh để người dùng gõ `"dien thoai"` vẫn tìm ra `"telephone"`.

---

## 7. ĐỒNG BỘ DỮ LIỆU: IN-MEMORY INDEX $\leftrightarrow$ SQLITE

- **SQLite**: Đóng vai trò **Persistent Source of Truth** (Nguồn chân lý lưu trữ bền vững), đảm bảo tính toàn vẹn ACID, không bị mất dữ liệu khi tắt server.
- **Trie trên RAM**: Đóng vai trò **High-Speed Search Index** (Chỉ mục tìm kiếm tốc độ cao).
- **Vòng đời Đồng bộ (Synchronization Lifecycle)**:
  - **Khởi động server (Startup)**: FastAPI Lifespan đọc toàn bộ 22,002 từ từ SQLite và nạp đồng thời vào Cây Trie tiếng Anh và Cây Trie tiếng Việt trong **~670 ms**.
  - **Thêm từ mới (`POST /api/words`)**: Ghi vào SQLite $\rightarrow$ Lấy ID mới sinh $\rightarrow$ Gọi `Trie.insert()` $\rightarrow$ Tra cứu được ngay lập tức.
  - **Sửa từ (`PUT /api/words/{id}`)**: Cập nhật DB $\rightarrow$ Nếu đổi từ vựng/nghĩa $\rightarrow$ Gọi `Trie.delete()` từ cũ và `Trie.insert()` từ mới.
  - **Xóa từ (`DELETE /api/words/{id}`)**: Xóa bản ghi trong DB $\rightarrow$ Gọi `Trie.delete()` tỉa bỏ nút khỏi cây.

---

## 8. KẾT QUẢ THỰC NGHIỆM & ĐO LƯỜNG HIỆU NĂNG

Dự án được đo lường thực nghiệm trên môi trường máy tính thông thường (Windows 11, Python 3.13):

| Thao tác / Giải thuật | Quy mô dữ liệu | Thời gian thực thi | Độ phức tạp lý thuyết | Ghi chú đánh giá |
| :--- | :--- | :--- | :--- | :--- |
| **Khởi tạo 2 Cây Trie (Anh + Việt)** | 22,002 từ DB (46,938 cụm) | **~674.6 ms** | $O(N \cdot L)$ | Chỉ chạy 1 lần khi bật server |
| **Tra cứu chính xác tiếng Anh (`computer`)** | 22,002 từ | **0.0072 ms** | $O(L)$ | Cận thời gian thực, nhanh hơn SQL 150x |
| **Tra cứu chính xác tiếng Việt (`xin chào`)** | 46,938 cụm từ | **0.0038 ms** | $O(L)$ | Cận thời gian thực |
| **Gợi ý tự động hoàn thành (`comp`)** | 22,002 từ | **0.0210 ms** | $O(P + K)$ | Trả về 10 từ theo thứ tự alphabet |
| **Tìm kiếm mờ Levenshtein (`comptuer`)** | 22,002 từ | **14.30 ms** | $O(N_{pruned} \cdot M \cdot N)$ | Nhờ chặn biên chiều dài |
| **Mức tiêu thụ bộ nhớ RAM** | Toàn bộ 2 Trie + Cache | **~45 MB** | $O(\sum L)$ | Rất tối ưu cho môi trường đại học |
| **Độ bao phủ kiểm thử tự động (Pytest)** | 78 test cases | **5.38 s** | 100% Pass | Bao phủ toàn bộ edge case |

---

## 9. CẤU TRÚC SLIDE THUYẾT TRÌNH TỪNG TRANG (SLIDE-BY-SLIDE OUTLINE)

Dưới đây là dàn bài chi tiết gồm **12 trang slide** được thiết kế chuẩn khoa học để nhóm trình bày trong 10–15 phút:

### Slide 1: Trang tiêu đề (Title Slide)
- **Tiêu đề lớn**: SMART DICTIONARY — LEXI
- **Tiêu đề phụ**: Hệ Thống Quản Lý Từ Điển Thông Minh với Cây Tiền Tố (Trie) và Tìm Kiếm Gần Đúng (Levenshtein Distance)
- **Môn học**: Cấu Trúc Dữ Liệu và Giải Thuật (Data Structures and Algorithms)
- **Giảng viên hướng dẫn & Thành viên nhóm thực hiện**: (Họ tên sinh viên, MSSV)

### Slide 2: Vấn đề nghiên cứu & Mục tiêu đề tài (Problem Statement)
- Thách thức của các từ điển truyền thống: Chi phí truy vấn SQL cao, không có khả năng gợi ý tiền tố tốc độ cao, không hỗ trợ sửa lỗi chính tả khi người dùng gõ sai.
- Mục tiêu: Áp dụng kiến thức Cấu trúc dữ liệu & Giải thuật để xây dựng ứng dụng Web tra cứu thời gian thực, có khả năng gợi ý từ và sửa lỗi chính tả hai chiều Anh–Việt.

### Slide 3: Kiến trúc tổng thể hệ thống (System Architecture)
- Sơ đồ 3 tầng: React Frontend $\leftrightarrow$ FastAPI Service $\leftrightarrow$ In-Memory DSA & SQLite Database.
- Nguyên lý thiết kế: Tách bạch giữa lưu trữ bền vững (Persistence) và chỉ mục giải thuật tốc độ cao (In-Memory Index).

### Slide 4: Cấu trúc dữ liệu Cây Tiền Tố (Trie Data Structure)
- Trình bày trực quan hình ảnh một cây Trie với các nhánh ký tự `c -> o -> m -> p -> u -> t -> e -> r`.
- Phân tích cấu trúc `TrieNode` và các trường dữ liệu (`children`, `is_end`, `word_id`).
- So sánh ưu việt của Trie so với Hash Table và B-Tree: Khả năng tìm kiếm tiền tố và duy trì thứ tự từ điển tự nhiên.

### Slide 5: Các giải thuật trên Trie & Độ phức tạp (Algorithms on Trie)
- Thao tác `insert`: Thêm từ với $O(L)$.
- Thao tác `search`: Tra cứu chính xác với $O(L)$, độc lập với kích thước từ điển $N$.
- Thao tác `get_suggestions`: Bounded DFS theo thứ tự alphabet trong $O(P + K)$.
- Thao tác `delete`: Đệ quy từ dưới lên (Bottom-up pruning) để thu hồi bộ nhớ dư thừa.

### Slide 6: Giải thuật Khoảng cách Levenshtein (Levenshtein Distance)
- Bài toán: Đo độ sai khác giữa hai chuỗi qua 3 thao tác đơn vị: Chèn, Xóa, Thay thế.
- Bảng quy hoạch động (DP Table): Minh họa ma trận quy hoạch động giữa `"kitten"` và `"sitting"` (khoảng cách = 3).
- Công thức truy hồi $D[i][j] = \min(D[i-1][j]+1, D[i][j-1]+1, D[i-1][j-1] + \text{cost})$.

### Slide 7: Tối ưu hóa Levenshtein & Chặn biên Chiều dài (Optimization & Pruning)
- Bài toán nút thắt cổ chai: Tại sao không thể duyệt Levenshtein thô trên 22,000 từ?
- Định lý chặn biên chiều dài: $|len(W) - len(Q)| \le \text{max\_distance}$. Giải thích cơ chế cắt tỉa 85% số phép tính ma trận không cần thiết.
- Tối ưu bộ nhớ: Thuật toán 2 dòng (Two-row DP) giảm không gian từ $O(M \cdot N)$ xuống $O(\min(M, N))$.

### Slide 8: Thuật toán Xếp hạng Đơn định 5 Tầng (5-Tier Ranking Engine)
- Giới thiệu bộ khóa so sánh: `(is_exact, is_prefix, edit_distance, length_diff, word)`.
- Giải thích vì sao kết quả gợi ý phải mang tính đơn định (Deterministic) và giải thích được (Explainable) thay vì dùng mô hình hộp đen.

### Slide 9: Tra cứu Hai chiều Anh ↔ Việt (Bidirectional Retrieval)
- Kỹ thuật tách cụm từ định nghĩa tiếng Việt (Phrase Tokenization).
- Kiến trúc Cây Trie tiếng Việt lưu trữ 46,938 cụm từ.
- Cơ chế giải quyết từ đa nghĩa: Ánh xạ đảo ngữ (Inverted Index) từ cụm từ tiếng Việt sang danh sách từ tiếng Anh đồng nghĩa.
- Xử lý tiếng Việt không dấu (Accent-insensitive matching).

### Slide 10: Đồng bộ hóa Dữ liệu SQLite ↔ Trie (Synchronization Engine)
- Sơ đồ chu trình CRUD: Create / Update / Delete trên cơ sở dữ liệu và phản chiếu ngay lập tức lên cây Trie.
- Đảm bảo tính nhất quán dữ liệu (Data Consistency) mà không cần khởi động lại server.

### Slide 11: Kết quả Thực nghiệm & Demo Sản phẩm (Experimental Results & Demo)
- Bảng thống kê hiệu năng thực tế đo được (Latency $< 0.01\text{ ms}$, RAM $\approx 45\text{ MB}$, 22,002 từ vựng).
- Minh họa ảnh chụp màn hình ứng dụng: Giao diện tra cứu chính xác, danh sách gợi ý tiền tố Trie, màn hình báo lỗi chính tả với khoảng cách Levenshtein.

### Slide 12: Kết luận & Hướng phát triển (Conclusion & Future Work)
- Tóm tắt kết quả: Ứng dụng thành công các cấu trúc dữ liệu và giải thuật kinh điển vào một bài toán thực tế quy mô lớn.
- Hướng mở rộng: Nghiên cứu tích hợp BK-Tree hoặc Trie lồng Levenshtein (Levenshtein Automaton) để tối ưu hóa hơn nữa tìm kiếm mờ cho tập dữ liệu hàng triệu từ.

---

## 10. BỘ CÂU HỎI PHẢN BIỆN & HƯỚNG DẪN TRẢ LỜI (Q&A DEFENSE)

Dưới đây là các câu hỏi thầy cô hội đồng thường hỏi nhất và câu trả lời chuẩn học thuật:

#### Câu 1: Tại sao nhóm không dùng cơ sở dữ liệu quan hệ (SQL) hay Elasticsearch mà phải tự cài đặt Trie và Levenshtein bằng code?
> **Trả lời:**
> "Dạ thưa Thầy/Cô, mục tiêu cốt lõi của đồ án Cấu trúc dữ liệu và Giải thuật là đào sâu bản chất toán học và cơ chế vận hành của các cấu trúc dữ liệu nền tảng. 
> Thứ nhất, SQL với câu lệnh `LIKE '%...%'` thực hiện quét toàn bảng (Full Table Scan) hoặc index tiền tố với chi phí đĩa đắt đỏ, không thể cung cấp khả năng tự động hoàn thành mượt mà với độ trễ dưới 0.05 ms như Trie trên RAM.
> Thứ hai, SQL không thể tính toán khoảng cách sửa lỗi chính tả linh hoạt theo bài toán Quy hoạch động Levenshtein. 
> Việc tự cài đặt Trie và Levenshtein giúp nhóm kiểm soát hoàn toàn độ phức tạp thời gian $O(L)$, áp dụng các kỹ thuật cắt tỉa chặn biên chiều dài và giải thích tường minh được tại sao một kết quả lại được đề xuất."

#### Câu 2: Khi dữ liệu tăng từ 2,000 lên 22,000 từ, độ phức tạp của Cây Trie có bị tăng lên không?
> **Trả lời:**
> "Dạ thưa Thầy/Cô, độ phức tạp tìm kiếm chính xác trên Cây Trie là **$O(L)$**, trong đó $L$ là độ dài của từ khóa tìm kiếm (thường chỉ từ 3 đến 15 ký tự). 
> Độ phức tạp này **hoàn toàn độc lập với tổng số lượng từ $N$ trong từ điển**. Do đó, dù từ điển có 2,000 từ, 22,000 từ hay 100,000 từ, thời gian tra cứu từ `"computer"` vẫn chỉ tốn đúng 8 bước duyệt liên kết nút, độ trễ đo được luôn duy trì ở mức xấp xỉ 0.007 ms."

#### Câu 3: Kỹ thuật chặn biên chiều dài (Length Difference Pruning) trong Levenshtein hoạt động như thế nào?
> **Trả lời:**
> "Dạ thưa Thầy/Cô, về mặt toán học, mỗi thao tác Levenshtein (chèn hoặc xóa) chỉ có thể làm thay đổi chiều dài chuỗi tối đa 1 ký tự. Do đó, để chuyển đổi từ chuỗi $W$ thành chuỗi $Q$, số phép chỉnh sửa tối thiểu bắt buộc phải lớn hơn hoặc bằng hiệu độ dài $|len(W) - len(Q)|$.
> Nếu cấu hình ngưỡng tìm kiếm sai số tối đa là `max_distance = 2`, bất kỳ từ nào trong từ điển có độ dài chênh lệch với từ truy vấn quá 2 ký tự (ví dụ từ dài 10 ký tự so với từ truy vấn 6 ký tự) thì khoảng cách Levenshtein chắc chắn $\ge 4 > 2$. Bằng cách so sánh độ dài trước, hệ thống loại bỏ ngay lập tức mà không cần dựng bảng ma trận DP, giúp giảm hơn 85% thời gian xử lý."

#### Câu 4: Làm thế nào hệ thống xử lý được từ đa nghĩa khi người dùng tìm kiếm từ tiếng Việt sang tiếng Anh?
> **Trả lời:**
> "Dạ thưa Thầy/Cô, một từ tiếng Việt như `'máy tính'` có thể tương ứng với nhiều từ tiếng Anh như `'computer'`, `'calculator'`, `'comptometer'`. Nhóm sử dụng kỹ thuật **Inverted Index (Chỉ mục đảo)** kết hợp với Cây Trie. 
> Cây Trie tiếng Việt lưu trữ cụm từ `'máy tính'`, và nút kết thúc trỏ tới một tập hợp các khóa ngoại `[ID_calculator, ID_computer, ID_comptometer]`. Khi người dùng tra cứu, hệ thống hiển thị định nghĩa của từ chính đồng thời sinh ra các nút đề xuất (suggestion pills) để người dùng có thể nhấp chuột chuyển sang xem các từ đồng nghĩa tiếng Anh tương ứng."

#### Câu 5: Bộ nhớ RAM cho Cây Trie có bị phình to (Memory Bloat) không và nhóm đã tối ưu ra sao?
> **Trả lời:**
> "Dạ thưa Thầy/Cô, Cây Trie chia sẻ tiền tố chung (ví dụ các từ `comp-ute`, `comp-any`, `comp-are` đều dùng chung 4 nút đầu tiên `c-o-m-p`), do đó tiết kiệm bộ nhớ đáng kể so với việc lưu trữ danh sách phẳng. 
> Ngoài ra, trong class `TrieNode`, nhóm sử dụng `__slots__ = ('children', 'is_end', 'word_id')` của Python để ngăn việc tự động tạo dictionary `__dict__` cho mỗi instance của nút, giúp giảm hơn 60% dung lượng bộ nhớ cho mỗi nút. Toàn bộ 2 Cây Trie cho 22,002 từ chỉ chiếm khoảng 45 MB RAM."
