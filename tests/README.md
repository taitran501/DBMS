# Hướng dẫn kiểm thử Python và TDD

Dự án dùng `pytest`. Test hiện tập trung vào các contract và workflow của phân hệ
Database Object trong bộ Mini DBMS chạy in-memory. Coverage cao không tự chứng
minh toàn bộ DBMS tuân thủ ACID, cũng không thay thế việc kiểm tra assertion và
các tình huống thất bại.

## Cấu trúc và cách chạy

- `tests/unit/`: kiểm tra một component hoặc contract độc lập.
- `tests/integration/`: kiểm tra workflow qua nhiều component.
- `tests/conftest.py`: tự gắn marker theo thư mục.

```bash
python -m pip install -r requirements-dev.txt
python -m pytest
python -m pytest -m unit
python -m pytest -m integration
python -m pytest --cov=dbms --cov-branch --cov-report=term-missing
```

Lệnh coverage phải đạt 100% statement và branch coverage. Unit và integration
được chạy riêng để phản hồi nhanh; quality gate đầy đủ chạy toàn bộ suite.

## Quy ước viết test

Tên test mô tả hành vi theo mẫu `test_<action>_<expected_result>`. Mỗi test chỉ
có một lý do chính để thất bại, không phụ thuộc thứ tự chạy hoặc state của test
khác.

### Arrange – Act – Assert

```python
def test_add_returns_sum():
    # Arrange
    left, right = 2, 3

    # Act
    result = add(left, right)

    # Assert
    assert result == 5
```

Nếu test ngắn, có thể bỏ comment nhưng vẫn giữ ba bước rõ ràng.

### Given – When – Then

Dùng dạng này khi viết requirement trước test:

```markdown
### COL-01: Không trả về column không tồn tại

Given một table `users` có column `id`.
When lấy column `email`.
Then raise `ValueError` và không thay đổi table.
```

## Quy trình Red – Green – Refactor

1. Ghi requirement bằng Given–When–Then và cấp ID.
2. Viết test nhỏ nhất mô tả hành vi, chạy riêng và xác nhận test fail đúng lý do
   (**Red**).
3. Viết implementation tối thiểu để test pass (**Green**).
4. Chạy test liên quan rồi toàn bộ suite.
5. Làm sạch code mà không đổi hành vi (**Refactor**) và chạy lại suite.
6. Cập nhật bảng truy vết bên dưới.

Khuyến nghị commit nhỏ theo thứ tự `test:` → `feat:` → `refactor:`. Không viết
lại lịch sử cũ để tạo cảm giác rằng code trước đây đã được phát triển bằng TDD.

## Truy vết requirement và test

| ID | Hành vi | Test | Loại |
|---|---|---|---|
| COL-01 | Column thiếu trong table tồn tại phải bị từ chối | `test_get_column_rejects_missing_column_in_existing_table` | Unit |
| DEP-01 | Dependency đệ quy không lặp khi graph hội tụ hoặc có vòng | `test_recursive_dependencies_are_unique_for_cycles_and_converging_paths` | Unit |
| META-01 | Metadata đăng ký được khi không truyền dependencies | `test_metadata_register_accepts_omitted_dependencies` | Unit |
| PROC-01 | Callable procedure từ chối sai số argument | `test_callable_procedure_rejects_wrong_argument_count` | Unit |
| REF-01 | `SET_NULL` cập nhật mọi dependent row | `test_set_null_updates_every_dependent_row` | Integration |
| REF-02 | Action chưa hỗ trợ không tự ý sửa dependent row | `test_unhandled_referential_action_leaves_dependent_rows_unchanged` | Integration |
| DML-01 | UNIQUE failure không để lại row lỗi | `test_unique_failure_is_atomic_and_ids_are_not_reused` | Integration |
| DML-02 | Trigger failure rollback thay đổi | `test_update_delete_and_trigger_failure_roll_back` | Integration |
| FK-01 | Child row chỉ được insert khi parent tồn tại | `test_insert_child_rejects_missing_parent_and_accepts_existing_parent` | Integration |
| CAT-01 | Table trùng tên bị từ chối | `test_create_table_rejects_duplicate_name` | Unit |

Khi thêm hành vi mới, thêm một dòng vào bảng sau khi hoàn thành chu trình TDD.
