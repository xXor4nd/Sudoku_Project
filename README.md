# Generalized Sudoku Benchmark & Comparative Study

Nghiên cứu thực nghiệm so sánh đa mô hình giải bài toán Sudoku tổng quát (N × N, với N ∈ {9, 16, 25, 36, 49}) giữa các trường phái:
- **SAT (PySAT):** Đánh giá 5 kỹ thuật mã hóa At-Most-One (Pairwise, Binary, Sequential Counter, Commander, Product).
- **Constraint Programming (CP):** Google OR-Tools CP-SAT (Lazy Clause Generation) và IBM CPLEX CP Optimizer.
- **Integer Linear Programming (ILP):** Gurobi Optimizer và IBM CPLEX MIP (0-1 formulation).

---

## 1. Environment

Khuyến nghị sử dụng Python 3.10+ và môi trường ảo:

```bash
# Tạo và kích hoạt môi trường ảo
python -m venv venv

# Windows:
venv\Scripts\activate

# Linux/macOS:
source venv/bin/activate

# Cài đặt các thư viện phụ thuộc
pip install -r requirements.txt
```

> **Lưu ý:** Gurobi (`gurobipy`) và IBM CPLEX (`docplex`) yêu cầu cài đặt phần mềm solver và giấy phép (license) tương ứng trên máy. Nếu không có giấy phép, hệ thống vẫn chạy bình thường với PySAT (SAT) và Google OR-Tools (CP).

---

## 2. Demo nhanh

File `main.py` cung cấp giao diện dòng lệnh để test nhanh thuật toán trên một bảng Sudoku:

```bash
# 1. Giải mặc định bảng 9x9 bằng PySAT Glucose4 (Sequential Counter)
python main.py

# 2. So sánh đối đầu 5 kỹ thuật mã hóa SAT AMO trên cùng một đề
python main.py --compare-amo

# 3. So sánh các trường phái giải (SAT vs CP vs ILP)
python main.py --cross-solvers

# 4. Thử nghiệm trên bảng kích thước lớn hơn (16x16 hoặc 25x25)
python main.py --size 16

# 5. Giải chuỗi đề tùy chỉnh (1 dòng)
python main.py --puzzle "4...3.......6..8..........1......."
```

---

## 3. Chạy Benchmark thực nghiệm

Script `scripts/benchmark_runner.py` là bộ điều phối benchmark chính, hỗ trợ timeout phân tầng, early stopping và tự động lưu kết quả vào CSV.

### Cú pháp cơ bản
```bash
python scripts/benchmark_runner.py [arguments]
```

### Các tham số dòng lệnh chính

| Tham số | Giá trị | Mặc định | Ý nghĩa |
| :--- | :--- | :--- | :--- |
| `--mode` | `sat_ablation`, `cross_solver`, `all` | `all` | Chế độ chạy: so sánh 5 mã hóa SAT (`sat_ablation`), so sánh giữa các solver (`cross_solver`), hoặc chạy cả hai (`all`). |
| `--source` | `dataset`, `generated` | `dataset` | Nguồn đề: đọc từ các file trong thư mục `data/` hoặc tự sinh ngẫu nhiên theo seed. |
| `--sizes` | Danh sách số nguyên (vd: `9 16 25`) | `9 16 25 36 49` | Kích thước ma trận cần đánh giá. |
| `--puzzles_per_size`| Số nguyên | `5` | Số lượng đề thử nghiệm cho mỗi kích thước khi chạy kiểm thử nhanh. |
| `--full_dataset` | Cờ (flag) | `False` | Chạy toàn bộ dữ liệu mẫu trong thư mục `data/` (100 đề 16x16, 40 đề 25x25, 20 đề 36x36, 10 đề 49x49). |
| `--puzzles_9x9` | Số nguyên | `5000` | Số lượng đề 9x9 lấy từ tập 17-clue khi dùng `--full_dataset`. |
| `--time_limit` | Số thực (giây) | `60.0` | Thời gian timeout tối đa cho mỗi solver trên 1 đề bài. |
| `--sat_solvers` | Danh sách engine PySAT | `glucose4` | Engine SAT solver (ví dụ: `glucose4`, `cadical195`, `minisat22`). |
| `--csv_output` | Đường dẫn file | `benchmark_results.csv` | Tên file CSV lưu chi tiết số biến, số mệnh đề, thời gian encode và thời gian giải. |
| `--no-plot` | Cờ (flag) | Tự vẽ đồ thị | Tắt bước tự động xuất biểu đồ sau khi benchmark kết thúc. |

### Ví dụ các lệnh benchmark thông dụng

```bash
# Test nhanh cả 3 trường phái trên kích thước 9x9 và 16x16 (mỗi size 5 đề)
python scripts/benchmark_runner.py --mode cross_solver --sizes 9 16 --puzzles_per_size 5

# Chạy riêng ablation study so sánh 5 kỹ thuật SAT AMO cho size 9x9, 16x16, 25x25
python scripts/benchmark_runner.py --mode sat_ablation --sizes 9 16 25 --puzzles_per_size 10

# Chạy toàn bộ dataset
python scripts/benchmark_runner.py --mode all --full_dataset --puzzles_9x9 5000
```

---

## 4. Trích xuất bảng số liệu LaTeX và đồ thị

```bash
# Đọc log benchmark_results.csv và xuất mã bảng LaTeX (Table 1, 2, 3 chuẩn Elsevier booktabs)
python scripts/generate_report_tables.py

# Kiểm tra độ chính xác và tính không mâu thuẫn của các file dataset trong data/
python utils/verifier.py
```

---

## 5. Structure

```text
├── data/
├── encoders/
├── solvers/      # PySAT, Google OR-Tools CP-SAT, Gurobi, CPLEX
├── utils/
├── scripts/
├── report_tables/
├── main.py       # test, demo
├── requirements.txt
└── benchmark_results.csv
```
