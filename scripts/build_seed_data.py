"""Build realistic English-Vietnamese dictionary dataset with 2,500+ authentic entries."""

import json
from pathlib import Path

# Base vocabulary components covering everyday, academic, and computer science domains
CORE_ENTRIES = [
    # Computer Science & Technology
    ("algorithm", "thuật toán", "/ˈæl.ɡə.rɪ.ðəm/", "noun", "An algorithm is a step-by-step procedure for solving a problem."),
    ("array", "mảng", "/əˈreɪ/", "noun", "An array stores elements of the same type in contiguous memory."),
    ("binary", "nhị phân", "/ˈbaɪ.nər.i/", "adjective", "Computers process data in binary format consisting of 0s and 1s."),
    ("cache", "bộ nhớ đệm", "/kæʃ/", "noun", "Fast memory used to speed up data access."),
    ("compiler", "trình biên dịch", "/kəmˈpaɪ.lər/", "noun", "A compiler translates high-level code into machine instructions."),
    ("database", "cơ sở dữ liệu", "/ˈdeɪ.tə.beɪs/", "noun", "A database organizes structured data for fast retrieval."),
    ("function", "hàm, chức năng", "/ˈfʌŋk.ʃən/", "noun", "A function encapsulates reusable logic."),
    ("graph", "đồ thị", "/ɡræf/", "noun", "A graph consists of vertices connected by edges."),
    ("hash", "băm", "/hæʃ/", "noun", "A hash table provides fast average-case lookup."),
    ("index", "chỉ mục", "/ˈɪn.deks/", "noun", "An index speeds up search queries on a database."),
    ("iteration", "vòng lặp, phép lặp", "/ˌɪt.əˈreɪ.ʃən/", "noun", "Each iteration processes one element of the collection."),
    ("loop", "vòng lặp", "/luːp/", "noun", "A loop repeats a code block until a condition is met."),
    ("memory", "bộ nhớ", "/ˈmem.ər.i/", "noun", "RAM is the primary volatile memory of a computer."),
    ("node", "nút", "/nəʊd/", "noun", "Each node in a linked list contains data and a pointer to the next node."),
    ("pointer", "con trỏ", "/ˈpɔɪn.tər/", "noun", "A pointer stores the memory address of another variable."),
    ("queue", "hàng đợi", "/kjuː/", "noun", "A queue follows the First-In, First-Out (FIFO) principle."),
    ("recursion", "đệ quy", "/rɪˈkɜː.ʃən/", "noun", "Recursion occurs when a function calls itself."),
    ("stack", "ngăn xếp", "/stæk/", "noun", "A stack operates on a Last-In, First-Out (LIFO) basis."),
    ("tree", "cây", "/triː/", "noun", "A tree is a hierarchical data structure with nodes and edges."),
    ("trie", "cây tiền tố", "/traɪ/", "noun", "A trie is an efficient tree structure for prefix search."),
    ("variable", "biến số", "/ˈveə.ri.ə.bəl/", "noun", "A variable holds a value that can be modified during program execution."),
    ("computer", "máy tính", "/kəmˈpjuː.tər/", "noun", "I use my computer every day for studying and programming."),
    ("network", "mạng lưới", "/ˈnet.wɜːk/", "noun", "The local area network connects all office workstations."),
    ("server", "máy chủ", "/ˈsɜː.vər/", "noun", "The web server responds to incoming HTTP requests."),
    ("client", "máy khách", "/ˈklaɪ.ənt/", "noun", "The browser acts as a client requesting web resources."),
    ("software", "phần mềm", "/ˈsɒft.weər/", "noun", "The software provides tools for image processing."),
    ("hardware", "phần cứng", "/ˈhɑːd.weər/", "noun", "CPU and RAM are vital hardware components."),
    ("program", "chương trình", "/ˈprəʊ.ɡræm/", "noun", "She wrote a Python program to analyze survey results."),
    ("debugger", "trình gỡ lỗi", "/diːˈbʌɡ.ər/", "noun", "Use a debugger to trace runtime errors."),
    ("system", "hệ thống", "/ˈsɪs.təm/", "noun", "The operating system coordinates system hardware and software."),
]

def generate_dictionary_entries():
    """Generates an initial dictionary with ~2,500 comprehensive entries."""
    from scripts.vocabulary_builder import get_full_vocabulary
    return get_full_vocabulary()

if __name__ == "__main__":
    print("Builder ready.")
