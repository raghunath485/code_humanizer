"""
Code Generation Engine
Generates code from natural language prompts using template matching.
Supports Python, C, C++, and Java output.
"""

from __future__ import annotations

import re


# ── Template registry ────────────────────────────────────────────────────────
# Each entry: (list of trigger keywords/phrases, generator function)
# Generator functions accept (language, **extracted_params) and return code str.

def _match_score(prompt: str, keywords: list[str]) -> int:
    """Count how many keywords appear in the prompt."""
    lower = prompt.lower()
    return sum(1 for kw in keywords if kw in lower)


# ── Code templates ───────────────────────────────────────────────────────────

def _hello_world(lang: str, **_kw: str) -> str:
    templates = {
        "python": 'print("Hello, World!")',
        "c": (
            '#include <stdio.h>\n\n'
            'int main() {\n'
            '    printf("Hello, World!\\n");\n'
            '    return 0;\n'
            '}'
        ),
        "cpp": (
            '#include <iostream>\n\n'
            'int main() {\n'
            '    std::cout << "Hello, World!" << std::endl;\n'
            '    return 0;\n'
            '}'
        ),
        "java": (
            'public class HelloWorld {\n'
            '    public static void main(String[] args) {\n'
            '        System.out.println("Hello, World!");\n'
            '    }\n'
            '}'
        ),
    }
    return templates.get(lang, templates["python"])


def _factorial(lang: str, **_kw: str) -> str:
    templates = {
        "python": (
            'def factorial(n):\n'
            '    """Calculate the factorial of n recursively."""\n'
            '    if n <= 1:\n'
            '        return 1\n'
            '    return n * factorial(n - 1)\n'
            '\n\n'
            'def factorial_iterative(n):\n'
            '    """Calculate the factorial of n iteratively."""\n'
            '    result = 1\n'
            '    for i in range(2, n + 1):\n'
            '        result *= i\n'
            '    return result\n'
            '\n\n'
            '# Example usage\n'
            'number = 5\n'
            'print(f"{number}! = {factorial(number)}")\n'
            'print(f"{number}! = {factorial_iterative(number)}")'
        ),
        "c": (
            '#include <stdio.h>\n\n'
            '// Recursive factorial\n'
            'long long factorial(int n) {\n'
            '    if (n <= 1) return 1;\n'
            '    return n * factorial(n - 1);\n'
            '}\n\n'
            '// Iterative factorial\n'
            'long long factorial_iterative(int n) {\n'
            '    long long result = 1;\n'
            '    for (int i = 2; i <= n; i++) {\n'
            '        result *= i;\n'
            '    }\n'
            '    return result;\n'
            '}\n\n'
            'int main() {\n'
            '    int number = 5;\n'
            '    printf("%d! = %lld\\n", number, factorial(number));\n'
            '    printf("%d! = %lld\\n", number, factorial_iterative(number));\n'
            '    return 0;\n'
            '}'
        ),
        "cpp": (
            '#include <iostream>\n\n'
            '// Recursive factorial\n'
            'long long factorial(int n) {\n'
            '    if (n <= 1) return 1;\n'
            '    return n * factorial(n - 1);\n'
            '}\n\n'
            '// Iterative factorial\n'
            'long long factorial_iterative(int n) {\n'
            '    long long result = 1;\n'
            '    for (int i = 2; i <= n; i++) {\n'
            '        result *= i;\n'
            '    }\n'
            '    return result;\n'
            '}\n\n'
            'int main() {\n'
            '    int number = 5;\n'
            '    std::cout << number << "! = " << factorial(number) << std::endl;\n'
            '    std::cout << number << "! = " << factorial_iterative(number) << std::endl;\n'
            '    return 0;\n'
            '}'
        ),
        "java": (
            'public class Factorial {\n'
            '    // Recursive factorial\n'
            '    public static long factorial(int n) {\n'
            '        if (n <= 1) return 1;\n'
            '        return n * factorial(n - 1);\n'
            '    }\n\n'
            '    // Iterative factorial\n'
            '    public static long factorialIterative(int n) {\n'
            '        long result = 1;\n'
            '        for (int i = 2; i <= n; i++) {\n'
            '            result *= i;\n'
            '        }\n'
            '        return result;\n'
            '    }\n\n'
            '    public static void main(String[] args) {\n'
            '        int number = 5;\n'
            '        System.out.println(number + "! = " + factorial(number));\n'
            '        System.out.println(number + "! = " + factorialIterative(number));\n'
            '    }\n'
            '}'
        ),
    }
    return templates.get(lang, templates["python"])


def _fibonacci(lang: str, **_kw: str) -> str:
    templates = {
        "python": (
            'def fibonacci(n):\n'
            '    """Generate first n Fibonacci numbers."""\n'
            '    sequence = []\n'
            '    a, b = 0, 1\n'
            '    for _ in range(n):\n'
            '        sequence.append(a)\n'
            '        a, b = b, a + b\n'
            '    return sequence\n'
            '\n\n'
            'def fibonacci_recursive(n):\n'
            '    """Return the nth Fibonacci number recursively."""\n'
            '    if n <= 0:\n'
            '        return 0\n'
            '    if n == 1:\n'
            '        return 1\n'
            '    return fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2)\n'
            '\n\n'
            '# Example usage\n'
            'print("First 10 Fibonacci numbers:", fibonacci(10))\n'
            'print("8th Fibonacci number:", fibonacci_recursive(8))'
        ),
        "c": (
            '#include <stdio.h>\n\n'
            '// Iterative Fibonacci sequence\n'
            'void fibonacci(int n) {\n'
            '    int a = 0, b = 1, temp;\n'
            '    printf("Fibonacci sequence: ");\n'
            '    for (int i = 0; i < n; i++) {\n'
            '        printf("%d ", a);\n'
            '        temp = a + b;\n'
            '        a = b;\n'
            '        b = temp;\n'
            '    }\n'
            '    printf("\\n");\n'
            '}\n\n'
            '// Recursive Fibonacci\n'
            'int fibonacci_recursive(int n) {\n'
            '    if (n <= 0) return 0;\n'
            '    if (n == 1) return 1;\n'
            '    return fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2);\n'
            '}\n\n'
            'int main() {\n'
            '    fibonacci(10);\n'
            '    printf("8th Fibonacci: %d\\n", fibonacci_recursive(8));\n'
            '    return 0;\n'
            '}'
        ),
        "cpp": (
            '#include <iostream>\n'
            '#include <vector>\n\n'
            '// Iterative Fibonacci\n'
            'std::vector<int> fibonacci(int n) {\n'
            '    std::vector<int> seq;\n'
            '    int a = 0, b = 1;\n'
            '    for (int i = 0; i < n; i++) {\n'
            '        seq.push_back(a);\n'
            '        int temp = a + b;\n'
            '        a = b;\n'
            '        b = temp;\n'
            '    }\n'
            '    return seq;\n'
            '}\n\n'
            '// Recursive Fibonacci\n'
            'int fibonacci_recursive(int n) {\n'
            '    if (n <= 0) return 0;\n'
            '    if (n == 1) return 1;\n'
            '    return fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2);\n'
            '}\n\n'
            'int main() {\n'
            '    auto seq = fibonacci(10);\n'
            '    std::cout << "Fibonacci: ";\n'
            '    for (int x : seq) std::cout << x << " ";\n'
            '    std::cout << std::endl;\n'
            '    std::cout << "8th Fibonacci: " << fibonacci_recursive(8) << std::endl;\n'
            '    return 0;\n'
            '}'
        ),
        "java": (
            'import java.util.ArrayList;\n\n'
            'public class Fibonacci {\n'
            '    // Iterative Fibonacci\n'
            '    public static ArrayList<Integer> fibonacci(int n) {\n'
            '        ArrayList<Integer> seq = new ArrayList<>();\n'
            '        int a = 0, b = 1;\n'
            '        for (int i = 0; i < n; i++) {\n'
            '            seq.add(a);\n'
            '            int temp = a + b;\n'
            '            a = b;\n'
            '            b = temp;\n'
            '        }\n'
            '        return seq;\n'
            '    }\n\n'
            '    // Recursive Fibonacci\n'
            '    public static int fibonacciRecursive(int n) {\n'
            '        if (n <= 0) return 0;\n'
            '        if (n == 1) return 1;\n'
            '        return fibonacciRecursive(n - 1) + fibonacciRecursive(n - 2);\n'
            '    }\n\n'
            '    public static void main(String[] args) {\n'
            '        System.out.println("Fibonacci: " + fibonacci(10));\n'
            '        System.out.println("8th Fibonacci: " + fibonacciRecursive(8));\n'
            '    }\n'
            '}'
        ),
    }
    return templates.get(lang, templates["python"])


def _bubble_sort(lang: str, **_kw: str) -> str:
    templates = {
        "python": (
            'def bubble_sort(arr):\n'
            '    """Sort a list using the Bubble Sort algorithm."""\n'
            '    n = len(arr)\n'
            '    for i in range(n):\n'
            '        swapped = False\n'
            '        for j in range(0, n - i - 1):\n'
            '            if arr[j] > arr[j + 1]:\n'
            '                arr[j], arr[j + 1] = arr[j + 1], arr[j]\n'
            '                swapped = True\n'
            '        if not swapped:\n'
            '            break\n'
            '    return arr\n'
            '\n\n'
            '# Example usage\n'
            'data = [64, 34, 25, 12, 22, 11, 90]\n'
            'print("Sorted:", bubble_sort(data))'
        ),
        "c": (
            '#include <stdio.h>\n\n'
            'void bubble_sort(int arr[], int n) {\n'
            '    for (int i = 0; i < n - 1; i++) {\n'
            '        int swapped = 0;\n'
            '        for (int j = 0; j < n - i - 1; j++) {\n'
            '            if (arr[j] > arr[j + 1]) {\n'
            '                int temp = arr[j];\n'
            '                arr[j] = arr[j + 1];\n'
            '                arr[j + 1] = temp;\n'
            '                swapped = 1;\n'
            '            }\n'
            '        }\n'
            '        if (!swapped) break;\n'
            '    }\n'
            '}\n\n'
            'int main() {\n'
            '    int arr[] = {64, 34, 25, 12, 22, 11, 90};\n'
            '    int n = sizeof(arr) / sizeof(arr[0]);\n'
            '    bubble_sort(arr, n);\n'
            '    printf("Sorted: ");\n'
            '    for (int i = 0; i < n; i++) printf("%d ", arr[i]);\n'
            '    printf("\\n");\n'
            '    return 0;\n'
            '}'
        ),
        "cpp": (
            '#include <iostream>\n'
            '#include <vector>\n\n'
            'void bubble_sort(std::vector<int>& arr) {\n'
            '    int n = arr.size();\n'
            '    for (int i = 0; i < n - 1; i++) {\n'
            '        bool swapped = false;\n'
            '        for (int j = 0; j < n - i - 1; j++) {\n'
            '            if (arr[j] > arr[j + 1]) {\n'
            '                std::swap(arr[j], arr[j + 1]);\n'
            '                swapped = true;\n'
            '            }\n'
            '        }\n'
            '        if (!swapped) break;\n'
            '    }\n'
            '}\n\n'
            'int main() {\n'
            '    std::vector<int> arr = {64, 34, 25, 12, 22, 11, 90};\n'
            '    bubble_sort(arr);\n'
            '    std::cout << "Sorted: ";\n'
            '    for (int x : arr) std::cout << x << " ";\n'
            '    std::cout << std::endl;\n'
            '    return 0;\n'
            '}'
        ),
        "java": (
            'public class BubbleSort {\n'
            '    public static void bubbleSort(int[] arr) {\n'
            '        int n = arr.length;\n'
            '        for (int i = 0; i < n - 1; i++) {\n'
            '            boolean swapped = false;\n'
            '            for (int j = 0; j < n - i - 1; j++) {\n'
            '                if (arr[j] > arr[j + 1]) {\n'
            '                    int temp = arr[j];\n'
            '                    arr[j] = arr[j + 1];\n'
            '                    arr[j + 1] = temp;\n'
            '                    swapped = true;\n'
            '                }\n'
            '            }\n'
            '            if (!swapped) break;\n'
            '        }\n'
            '    }\n\n'
            '    public static void main(String[] args) {\n'
            '        int[] arr = {64, 34, 25, 12, 22, 11, 90};\n'
            '        bubbleSort(arr);\n'
            '        System.out.print("Sorted: ");\n'
            '        for (int x : arr) System.out.print(x + " ");\n'
            '        System.out.println();\n'
            '    }\n'
            '}'
        ),
    }
    return templates.get(lang, templates["python"])


def _binary_search(lang: str, **_kw: str) -> str:
    templates = {
        "python": (
            'def binary_search(arr, target):\n'
            '    """Search for target in a sorted list using Binary Search."""\n'
            '    left, right = 0, len(arr) - 1\n'
            '    while left <= right:\n'
            '        mid = (left + right) // 2\n'
            '        if arr[mid] == target:\n'
            '            return mid\n'
            '        elif arr[mid] < target:\n'
            '            left = mid + 1\n'
            '        else:\n'
            '            right = mid - 1\n'
            '    return -1\n'
            '\n\n'
            '# Example usage\n'
            'data = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]\n'
            'target = 23\n'
            'result = binary_search(data, target)\n'
            'print(f"Found {target} at index {result}" if result != -1 else f"{target} not found")'
        ),
        "c": (
            '#include <stdio.h>\n\n'
            'int binary_search(int arr[], int n, int target) {\n'
            '    int left = 0, right = n - 1;\n'
            '    while (left <= right) {\n'
            '        int mid = left + (right - left) / 2;\n'
            '        if (arr[mid] == target) return mid;\n'
            '        else if (arr[mid] < target) left = mid + 1;\n'
            '        else right = mid - 1;\n'
            '    }\n'
            '    return -1;\n'
            '}\n\n'
            'int main() {\n'
            '    int arr[] = {2, 5, 8, 12, 16, 23, 38, 56, 72, 91};\n'
            '    int n = sizeof(arr) / sizeof(arr[0]);\n'
            '    int target = 23;\n'
            '    int result = binary_search(arr, n, target);\n'
            '    if (result != -1)\n'
            '        printf("Found %d at index %d\\n", target, result);\n'
            '    else\n'
            '        printf("%d not found\\n", target);\n'
            '    return 0;\n'
            '}'
        ),
        "cpp": (
            '#include <iostream>\n'
            '#include <vector>\n\n'
            'int binary_search(const std::vector<int>& arr, int target) {\n'
            '    int left = 0, right = arr.size() - 1;\n'
            '    while (left <= right) {\n'
            '        int mid = left + (right - left) / 2;\n'
            '        if (arr[mid] == target) return mid;\n'
            '        else if (arr[mid] < target) left = mid + 1;\n'
            '        else right = mid - 1;\n'
            '    }\n'
            '    return -1;\n'
            '}\n\n'
            'int main() {\n'
            '    std::vector<int> arr = {2, 5, 8, 12, 16, 23, 38, 56, 72, 91};\n'
            '    int target = 23;\n'
            '    int result = binary_search(arr, target);\n'
            '    if (result != -1)\n'
            '        std::cout << "Found " << target << " at index " << result << std::endl;\n'
            '    else\n'
            '        std::cout << target << " not found" << std::endl;\n'
            '    return 0;\n'
            '}'
        ),
        "java": (
            'public class BinarySearch {\n'
            '    public static int binarySearch(int[] arr, int target) {\n'
            '        int left = 0, right = arr.length - 1;\n'
            '        while (left <= right) {\n'
            '            int mid = left + (right - left) / 2;\n'
            '            if (arr[mid] == target) return mid;\n'
            '            else if (arr[mid] < target) left = mid + 1;\n'
            '            else right = mid - 1;\n'
            '        }\n'
            '        return -1;\n'
            '    }\n\n'
            '    public static void main(String[] args) {\n'
            '        int[] arr = {2, 5, 8, 12, 16, 23, 38, 56, 72, 91};\n'
            '        int target = 23;\n'
            '        int result = binarySearch(arr, target);\n'
            '        System.out.println(result != -1 ?\n'
            '            "Found " + target + " at index " + result :\n'
            '            target + " not found");\n'
            '    }\n'
            '}'
        ),
    }
    return templates.get(lang, templates["python"])


def _prime_check(lang: str, **_kw: str) -> str:
    templates = {
        "python": (
            'def is_prime(n):\n'
            '    """Check if a number is prime."""\n'
            '    if n < 2:\n'
            '        return False\n'
            '    for i in range(2, int(n ** 0.5) + 1):\n'
            '        if n % i == 0:\n'
            '            return False\n'
            '    return True\n'
            '\n\n'
            'def primes_up_to(limit):\n'
            '    """Generate all primes up to a given limit (Sieve of Eratosthenes)."""\n'
            '    sieve = [True] * (limit + 1)\n'
            '    sieve[0] = sieve[1] = False\n'
            '    for i in range(2, int(limit ** 0.5) + 1):\n'
            '        if sieve[i]:\n'
            '            for j in range(i * i, limit + 1, i):\n'
            '                sieve[j] = False\n'
            '    return [i for i, v in enumerate(sieve) if v]\n'
            '\n\n'
            '# Example usage\n'
            'print("Is 17 prime?", is_prime(17))\n'
            'print("Primes up to 50:", primes_up_to(50))'
        ),
        "c": (
            '#include <stdio.h>\n'
            '#include <math.h>\n'
            '#include <stdbool.h>\n\n'
            'bool is_prime(int n) {\n'
            '    if (n < 2) return false;\n'
            '    for (int i = 2; i <= (int)sqrt(n); i++) {\n'
            '        if (n % i == 0) return false;\n'
            '    }\n'
            '    return true;\n'
            '}\n\n'
            'int main() {\n'
            '    printf("Is 17 prime? %s\\n", is_prime(17) ? "Yes" : "No");\n'
            '    printf("Primes up to 50: ");\n'
            '    for (int i = 2; i <= 50; i++) {\n'
            '        if (is_prime(i)) printf("%d ", i);\n'
            '    }\n'
            '    printf("\\n");\n'
            '    return 0;\n'
            '}'
        ),
        "cpp": (
            '#include <iostream>\n'
            '#include <cmath>\n'
            '#include <vector>\n\n'
            'bool is_prime(int n) {\n'
            '    if (n < 2) return false;\n'
            '    for (int i = 2; i <= (int)std::sqrt(n); i++) {\n'
            '        if (n % i == 0) return false;\n'
            '    }\n'
            '    return true;\n'
            '}\n\n'
            'int main() {\n'
            '    std::cout << "Is 17 prime? " << (is_prime(17) ? "Yes" : "No") << std::endl;\n'
            '    std::cout << "Primes up to 50: ";\n'
            '    for (int i = 2; i <= 50; i++) {\n'
            '        if (is_prime(i)) std::cout << i << " ";\n'
            '    }\n'
            '    std::cout << std::endl;\n'
            '    return 0;\n'
            '}'
        ),
        "java": (
            'public class PrimeCheck {\n'
            '    public static boolean isPrime(int n) {\n'
            '        if (n < 2) return false;\n'
            '        for (int i = 2; i <= Math.sqrt(n); i++) {\n'
            '            if (n % i == 0) return false;\n'
            '        }\n'
            '        return true;\n'
            '    }\n\n'
            '    public static void main(String[] args) {\n'
            '        System.out.println("Is 17 prime? " + isPrime(17));\n'
            '        System.out.print("Primes up to 50: ");\n'
            '        for (int i = 2; i <= 50; i++) {\n'
            '            if (isPrime(i)) System.out.print(i + " ");\n'
            '        }\n'
            '        System.out.println();\n'
            '    }\n'
            '}'
        ),
    }
    return templates.get(lang, templates["python"])


def _linked_list(lang: str, **_kw: str) -> str:
    templates = {
        "python": (
            'class Node:\n'
            '    """A node in a singly linked list."""\n'
            '    def __init__(self, data):\n'
            '        self.data = data\n'
            '        self.next = None\n'
            '\n\n'
            'class LinkedList:\n'
            '    """Singly linked list with common operations."""\n'
            '    def __init__(self):\n'
            '        self.head = None\n'
            '\n'
            '    def append(self, data):\n'
            '        new_node = Node(data)\n'
            '        if not self.head:\n'
            '            self.head = new_node\n'
            '            return\n'
            '        current = self.head\n'
            '        while current.next:\n'
            '            current = current.next\n'
            '        current.next = new_node\n'
            '\n'
            '    def display(self):\n'
            '        elements = []\n'
            '        current = self.head\n'
            '        while current:\n'
            '            elements.append(str(current.data))\n'
            '            current = current.next\n'
            '        print(" -> ".join(elements) + " -> None")\n'
            '\n'
            '    def delete(self, key):\n'
            '        current = self.head\n'
            '        if current and current.data == key:\n'
            '            self.head = current.next\n'
            '            return\n'
            '        prev = None\n'
            '        while current and current.data != key:\n'
            '            prev = current\n'
            '            current = current.next\n'
            '        if current:\n'
            '            prev.next = current.next\n'
            '\n\n'
            '# Example usage\n'
            'll = LinkedList()\n'
            'for val in [10, 20, 30, 40]:\n'
            '    ll.append(val)\n'
            'll.display()\n'
            'll.delete(20)\n'
            'll.display()'
        ),
        "c": (
            '#include <stdio.h>\n'
            '#include <stdlib.h>\n\n'
            'typedef struct Node {\n'
            '    int data;\n'
            '    struct Node* next;\n'
            '} Node;\n\n'
            'Node* create_node(int data) {\n'
            '    Node* node = (Node*)malloc(sizeof(Node));\n'
            '    node->data = data;\n'
            '    node->next = NULL;\n'
            '    return node;\n'
            '}\n\n'
            'void append(Node** head, int data) {\n'
            '    Node* new_node = create_node(data);\n'
            '    if (*head == NULL) { *head = new_node; return; }\n'
            '    Node* current = *head;\n'
            '    while (current->next) current = current->next;\n'
            '    current->next = new_node;\n'
            '}\n\n'
            'void display(Node* head) {\n'
            '    Node* current = head;\n'
            '    while (current) {\n'
            '        printf("%d -> ", current->data);\n'
            '        current = current->next;\n'
            '    }\n'
            '    printf("NULL\\n");\n'
            '}\n\n'
            'int main() {\n'
            '    Node* head = NULL;\n'
            '    append(&head, 10);\n'
            '    append(&head, 20);\n'
            '    append(&head, 30);\n'
            '    display(head);\n'
            '    return 0;\n'
            '}'
        ),
        "cpp": (
            '#include <iostream>\n\n'
            'struct Node {\n'
            '    int data;\n'
            '    Node* next;\n'
            '    Node(int val) : data(val), next(nullptr) {}\n'
            '};\n\n'
            'class LinkedList {\n'
            'public:\n'
            '    Node* head = nullptr;\n\n'
            '    void append(int data) {\n'
            '        Node* node = new Node(data);\n'
            '        if (!head) { head = node; return; }\n'
            '        Node* curr = head;\n'
            '        while (curr->next) curr = curr->next;\n'
            '        curr->next = node;\n'
            '    }\n\n'
            '    void display() {\n'
            '        Node* curr = head;\n'
            '        while (curr) {\n'
            '            std::cout << curr->data << " -> ";\n'
            '            curr = curr->next;\n'
            '        }\n'
            '        std::cout << "nullptr" << std::endl;\n'
            '    }\n'
            '};\n\n'
            'int main() {\n'
            '    LinkedList ll;\n'
            '    ll.append(10); ll.append(20); ll.append(30);\n'
            '    ll.display();\n'
            '    return 0;\n'
            '}'
        ),
        "java": (
            'public class LinkedList {\n'
            '    static class Node {\n'
            '        int data;\n'
            '        Node next;\n'
            '        Node(int data) { this.data = data; this.next = null; }\n'
            '    }\n\n'
            '    private Node head;\n\n'
            '    public void append(int data) {\n'
            '        Node node = new Node(data);\n'
            '        if (head == null) { head = node; return; }\n'
            '        Node curr = head;\n'
            '        while (curr.next != null) curr = curr.next;\n'
            '        curr.next = node;\n'
            '    }\n\n'
            '    public void display() {\n'
            '        Node curr = head;\n'
            '        while (curr != null) {\n'
            '            System.out.print(curr.data + " -> ");\n'
            '            curr = curr.next;\n'
            '        }\n'
            '        System.out.println("null");\n'
            '    }\n\n'
            '    public static void main(String[] args) {\n'
            '        LinkedList ll = new LinkedList();\n'
            '        ll.append(10); ll.append(20); ll.append(30);\n'
            '        ll.display();\n'
            '    }\n'
            '}'
        ),
    }
    return templates.get(lang, templates["python"])


def _stack(lang: str, **_kw: str) -> str:
    templates = {
        "python": (
            'class Stack:\n'
            '    """Stack implementation using a list."""\n'
            '    def __init__(self):\n'
            '        self.items = []\n'
            '\n'
            '    def push(self, item):\n'
            '        self.items.append(item)\n'
            '\n'
            '    def pop(self):\n'
            '        if self.is_empty():\n'
            '            raise IndexError("Stack is empty")\n'
            '        return self.items.pop()\n'
            '\n'
            '    def peek(self):\n'
            '        if self.is_empty():\n'
            '            raise IndexError("Stack is empty")\n'
            '        return self.items[-1]\n'
            '\n'
            '    def is_empty(self):\n'
            '        return len(self.items) == 0\n'
            '\n'
            '    def size(self):\n'
            '        return len(self.items)\n'
            '\n\n'
            '# Example usage\n'
            's = Stack()\n'
            'for val in [10, 20, 30]:\n'
            '    s.push(val)\n'
            'print("Top:", s.peek())\n'
            'print("Popped:", s.pop())\n'
            'print("Size:", s.size())'
        ),
        "c": (
            '#include <stdio.h>\n'
            '#include <stdlib.h>\n'
            '#include <stdbool.h>\n\n'
            '#define MAX_SIZE 100\n\n'
            'typedef struct {\n'
            '    int items[MAX_SIZE];\n'
            '    int top;\n'
            '} Stack;\n\n'
            'void init(Stack* s) { s->top = -1; }\n'
            'bool is_empty(Stack* s) { return s->top == -1; }\n'
            'bool is_full(Stack* s) { return s->top == MAX_SIZE - 1; }\n\n'
            'void push(Stack* s, int item) {\n'
            '    if (is_full(s)) { printf("Stack overflow\\n"); return; }\n'
            '    s->items[++s->top] = item;\n'
            '}\n\n'
            'int pop(Stack* s) {\n'
            '    if (is_empty(s)) { printf("Stack underflow\\n"); return -1; }\n'
            '    return s->items[s->top--];\n'
            '}\n\n'
            'int main() {\n'
            '    Stack s;\n'
            '    init(&s);\n'
            '    push(&s, 10); push(&s, 20); push(&s, 30);\n'
            '    printf("Popped: %d\\n", pop(&s));\n'
            '    printf("Popped: %d\\n", pop(&s));\n'
            '    return 0;\n'
            '}'
        ),
        "cpp": (
            '#include <iostream>\n'
            '#include <stack>\n\n'
            'int main() {\n'
            '    std::stack<int> s;\n'
            '    s.push(10); s.push(20); s.push(30);\n\n'
            '    std::cout << "Top: " << s.top() << std::endl;\n'
            '    s.pop();\n'
            '    std::cout << "After pop, top: " << s.top() << std::endl;\n'
            '    std::cout << "Size: " << s.size() << std::endl;\n'
            '    return 0;\n'
            '}'
        ),
        "java": (
            'import java.util.Stack;\n\n'
            'public class StackExample {\n'
            '    public static void main(String[] args) {\n'
            '        Stack<Integer> stack = new Stack<>();\n'
            '        stack.push(10); stack.push(20); stack.push(30);\n\n'
            '        System.out.println("Top: " + stack.peek());\n'
            '        System.out.println("Popped: " + stack.pop());\n'
            '        System.out.println("Size: " + stack.size());\n'
            '    }\n'
            '}'
        ),
    }
    return templates.get(lang, templates["python"])


def _reverse_string(lang: str, **_kw: str) -> str:
    templates = {
        "python": (
            'def reverse_string(s):\n'
            '    """Reverse a string using slicing."""\n'
            '    return s[::-1]\n'
            '\n\n'
            'def reverse_string_manual(s):\n'
            '    """Reverse a string character by character."""\n'
            '    chars = list(s)\n'
            '    left, right = 0, len(chars) - 1\n'
            '    while left < right:\n'
            '        chars[left], chars[right] = chars[right], chars[left]\n'
            '        left += 1\n'
            '        right -= 1\n'
            '    return "".join(chars)\n'
            '\n\n'
            '# Example usage\n'
            'text = "Hello, World!"\n'
            'print("Reversed:", reverse_string(text))\n'
            'print("Reversed:", reverse_string_manual(text))'
        ),
        "c": (
            '#include <stdio.h>\n'
            '#include <string.h>\n\n'
            'void reverse_string(char* str) {\n'
            '    int left = 0, right = strlen(str) - 1;\n'
            '    while (left < right) {\n'
            '        char temp = str[left];\n'
            '        str[left] = str[right];\n'
            '        str[right] = temp;\n'
            '        left++; right--;\n'
            '    }\n'
            '}\n\n'
            'int main() {\n'
            '    char str[] = "Hello, World!";\n'
            '    reverse_string(str);\n'
            '    printf("Reversed: %s\\n", str);\n'
            '    return 0;\n'
            '}'
        ),
        "cpp": (
            '#include <iostream>\n'
            '#include <algorithm>\n'
            '#include <string>\n\n'
            'int main() {\n'
            '    std::string str = "Hello, World!";\n'
            '    std::string reversed = str;\n'
            '    std::reverse(reversed.begin(), reversed.end());\n'
            '    std::cout << "Reversed: " << reversed << std::endl;\n'
            '    return 0;\n'
            '}'
        ),
        "java": (
            'public class ReverseString {\n'
            '    public static void main(String[] args) {\n'
            '        String str = "Hello, World!";\n'
            '        String reversed = new StringBuilder(str).reverse().toString();\n'
            '        System.out.println("Reversed: " + reversed);\n'
            '    }\n'
            '}'
        ),
    }
    return templates.get(lang, templates["python"])


def _palindrome(lang: str, **_kw: str) -> str:
    templates = {
        "python": (
            'def is_palindrome(s):\n'
            '    """Check if a string is a palindrome (ignoring case and spaces)."""\n'
            '    cleaned = "".join(c.lower() for c in s if c.isalnum())\n'
            '    return cleaned == cleaned[::-1]\n'
            '\n\n'
            '# Example usage\n'
            'tests = ["racecar", "hello", "A man a plan a canal Panama"]\n'
            'for text in tests:\n'
            '    print(f\'"{text}" → palindrome: {is_palindrome(text)}\')'
        ),
        "c": (
            '#include <stdio.h>\n'
            '#include <string.h>\n'
            '#include <ctype.h>\n'
            '#include <stdbool.h>\n\n'
            'bool is_palindrome(const char* str) {\n'
            '    int left = 0, right = strlen(str) - 1;\n'
            '    while (left < right) {\n'
            '        while (left < right && !isalnum(str[left])) left++;\n'
            '        while (left < right && !isalnum(str[right])) right--;\n'
            '        if (tolower(str[left]) != tolower(str[right])) return false;\n'
            '        left++; right--;\n'
            '    }\n'
            '    return true;\n'
            '}\n\n'
            'int main() {\n'
            '    printf("racecar: %s\\n", is_palindrome("racecar") ? "yes" : "no");\n'
            '    printf("hello: %s\\n", is_palindrome("hello") ? "yes" : "no");\n'
            '    return 0;\n'
            '}'
        ),
        "cpp": (
            '#include <iostream>\n'
            '#include <algorithm>\n'
            '#include <cctype>\n\n'
            'bool is_palindrome(const std::string& s) {\n'
            '    std::string cleaned;\n'
            '    for (char c : s)\n'
            '        if (std::isalnum(c)) cleaned += std::tolower(c);\n'
            '    std::string rev = cleaned;\n'
            '    std::reverse(rev.begin(), rev.end());\n'
            '    return cleaned == rev;\n'
            '}\n\n'
            'int main() {\n'
            '    std::cout << "racecar: " << (is_palindrome("racecar") ? "yes" : "no") << std::endl;\n'
            '    std::cout << "hello: " << (is_palindrome("hello") ? "yes" : "no") << std::endl;\n'
            '    return 0;\n'
            '}'
        ),
        "java": (
            'public class Palindrome {\n'
            '    public static boolean isPalindrome(String s) {\n'
            '        String cleaned = s.replaceAll("[^a-zA-Z0-9]", "").toLowerCase();\n'
            '        return cleaned.equals(new StringBuilder(cleaned).reverse().toString());\n'
            '    }\n\n'
            '    public static void main(String[] args) {\n'
            '        System.out.println("racecar: " + isPalindrome("racecar"));\n'
            '        System.out.println("hello: " + isPalindrome("hello"));\n'
            '    }\n'
            '}'
        ),
    }
    return templates.get(lang, templates["python"])


def _calculator(lang: str, **_kw: str) -> str:
    templates = {
        "python": (
            'def calculator():\n'
            '    """Simple calculator with basic operations."""\n'
            '    print("Simple Calculator")\n'
            '    print("Operations: +, -, *, /")\n'
            '    \n'
            '    num1 = float(input("Enter first number: "))\n'
            '    op = input("Enter operator (+, -, *, /): ")\n'
            '    num2 = float(input("Enter second number: "))\n'
            '    \n'
            '    if op == "+":\n'
            '        result = num1 + num2\n'
            '    elif op == "-":\n'
            '        result = num1 - num2\n'
            '    elif op == "*":\n'
            '        result = num1 * num2\n'
            '    elif op == "/":\n'
            '        result = num1 / num2 if num2 != 0 else "Error: Division by zero"\n'
            '    else:\n'
            '        result = "Invalid operator"\n'
            '    \n'
            '    print(f"Result: {num1} {op} {num2} = {result}")\n'
            '\n\n'
            'calculator()'
        ),
        "c": (
            '#include <stdio.h>\n\n'
            'int main() {\n'
            '    double num1, num2, result;\n'
            '    char op;\n\n'
            '    printf("Enter: number operator number\\n");\n'
            '    scanf("%lf %c %lf", &num1, &op, &num2);\n\n'
            '    switch (op) {\n'
            '        case \'+\': result = num1 + num2; break;\n'
            '        case \'-\': result = num1 - num2; break;\n'
            '        case \'*\': result = num1 * num2; break;\n'
            '        case \'/\':\n'
            '            if (num2 != 0) result = num1 / num2;\n'
            '            else { printf("Error: Division by zero\\n"); return 1; }\n'
            '            break;\n'
            '        default: printf("Invalid operator\\n"); return 1;\n'
            '    }\n'
            '    printf("%.2f %c %.2f = %.2f\\n", num1, op, num2, result);\n'
            '    return 0;\n'
            '}'
        ),
        "cpp": (
            '#include <iostream>\n\n'
            'int main() {\n'
            '    double num1, num2;\n'
            '    char op;\n\n'
            '    std::cout << "Enter: number operator number" << std::endl;\n'
            '    std::cin >> num1 >> op >> num2;\n\n'
            '    double result;\n'
            '    switch (op) {\n'
            '        case \'+\': result = num1 + num2; break;\n'
            '        case \'-\': result = num1 - num2; break;\n'
            '        case \'*\': result = num1 * num2; break;\n'
            '        case \'/\':\n'
            '            if (num2 != 0) result = num1 / num2;\n'
            '            else { std::cout << "Error: Division by zero" << std::endl; return 1; }\n'
            '            break;\n'
            '        default: std::cout << "Invalid operator" << std::endl; return 1;\n'
            '    }\n'
            '    std::cout << num1 << " " << op << " " << num2 << " = " << result << std::endl;\n'
            '    return 0;\n'
            '}'
        ),
        "java": (
            'import java.util.Scanner;\n\n'
            'public class Calculator {\n'
            '    public static void main(String[] args) {\n'
            '        Scanner sc = new Scanner(System.in);\n'
            '        System.out.println("Enter: number operator number");\n'
            '        double num1 = sc.nextDouble();\n'
            '        char op = sc.next().charAt(0);\n'
            '        double num2 = sc.nextDouble();\n'
            '        double result;\n\n'
            '        switch (op) {\n'
            '            case \'+\': result = num1 + num2; break;\n'
            '            case \'-\': result = num1 - num2; break;\n'
            '            case \'*\': result = num1 * num2; break;\n'
            '            case \'/\':\n'
            '                if (num2 != 0) result = num1 / num2;\n'
            '                else { System.out.println("Error: Division by zero"); return; }\n'
            '                break;\n'
            '            default: System.out.println("Invalid operator"); return;\n'
            '        }\n'
            '        System.out.println(num1 + " " + op + " " + num2 + " = " + result);\n'
            '    }\n'
            '}'
        ),
    }
    return templates.get(lang, templates["python"])


def _file_read_write(lang: str, **_kw: str) -> str:
    templates = {
        "python": (
            '# Writing to a file\n'
            'with open("output.txt", "w") as f:\n'
            '    f.write("Hello, World!\\n")\n'
            '    f.write("This is a test file.\\n")\n'
            '\n'
            '# Reading from a file\n'
            'with open("output.txt", "r") as f:\n'
            '    content = f.read()\n'
            '    print("File contents:")\n'
            '    print(content)\n'
            '\n'
            '# Reading line by line\n'
            'with open("output.txt", "r") as f:\n'
            '    for line_number, line in enumerate(f, 1):\n'
            '        print(f"Line {line_number}: {line.strip()}")'
        ),
        "c": (
            '#include <stdio.h>\n\n'
            'int main() {\n'
            '    // Writing to a file\n'
            '    FILE* fp = fopen("output.txt", "w");\n'
            '    if (fp == NULL) { printf("Error opening file\\n"); return 1; }\n'
            '    fprintf(fp, "Hello, World!\\n");\n'
            '    fprintf(fp, "This is a test file.\\n");\n'
            '    fclose(fp);\n\n'
            '    // Reading from a file\n'
            '    fp = fopen("output.txt", "r");\n'
            '    char line[256];\n'
            '    printf("File contents:\\n");\n'
            '    while (fgets(line, sizeof(line), fp)) {\n'
            '        printf("%s", line);\n'
            '    }\n'
            '    fclose(fp);\n'
            '    return 0;\n'
            '}'
        ),
        "cpp": (
            '#include <iostream>\n'
            '#include <fstream>\n'
            '#include <string>\n\n'
            'int main() {\n'
            '    // Writing\n'
            '    std::ofstream out("output.txt");\n'
            '    out << "Hello, World!" << std::endl;\n'
            '    out << "This is a test file." << std::endl;\n'
            '    out.close();\n\n'
            '    // Reading\n'
            '    std::ifstream in("output.txt");\n'
            '    std::string line;\n'
            '    std::cout << "File contents:" << std::endl;\n'
            '    while (std::getline(in, line)) {\n'
            '        std::cout << line << std::endl;\n'
            '    }\n'
            '    in.close();\n'
            '    return 0;\n'
            '}'
        ),
        "java": (
            'import java.io.*;\n\n'
            'public class FileIO {\n'
            '    public static void main(String[] args) throws IOException {\n'
            '        // Writing\n'
            '        BufferedWriter writer = new BufferedWriter(new FileWriter("output.txt"));\n'
            '        writer.write("Hello, World!\\n");\n'
            '        writer.write("This is a test file.\\n");\n'
            '        writer.close();\n\n'
            '        // Reading\n'
            '        BufferedReader reader = new BufferedReader(new FileReader("output.txt"));\n'
            '        String line;\n'
            '        System.out.println("File contents:");\n'
            '        while ((line = reader.readLine()) != null) {\n'
            '            System.out.println(line);\n'
            '        }\n'
            '        reader.close();\n'
            '    }\n'
            '}'
        ),
    }
    return templates.get(lang, templates["python"])


def _matrix_multiply(lang: str, **_kw: str) -> str:
    templates = {
        "python": (
            'def matrix_multiply(a, b):\n'
            '    """Multiply two matrices."""\n'
            '    rows_a, cols_a = len(a), len(a[0])\n'
            '    rows_b, cols_b = len(b), len(b[0])\n'
            '    if cols_a != rows_b:\n'
            '        raise ValueError("Incompatible matrix dimensions")\n'
            '    result = [[0] * cols_b for _ in range(rows_a)]\n'
            '    for i in range(rows_a):\n'
            '        for j in range(cols_b):\n'
            '            for k in range(cols_a):\n'
            '                result[i][j] += a[i][k] * b[k][j]\n'
            '    return result\n'
            '\n\n'
            '# Example usage\n'
            'a = [[1, 2], [3, 4]]\n'
            'b = [[5, 6], [7, 8]]\n'
            'result = matrix_multiply(a, b)\n'
            'for row in result:\n'
            '    print(row)'
        ),
        "c": (
            '#include <stdio.h>\n\n'
            '#define N 2\n\n'
            'void matrix_multiply(int a[N][N], int b[N][N], int result[N][N]) {\n'
            '    for (int i = 0; i < N; i++)\n'
            '        for (int j = 0; j < N; j++) {\n'
            '            result[i][j] = 0;\n'
            '            for (int k = 0; k < N; k++)\n'
            '                result[i][j] += a[i][k] * b[k][j];\n'
            '        }\n'
            '}\n\n'
            'int main() {\n'
            '    int a[N][N] = {{1, 2}, {3, 4}};\n'
            '    int b[N][N] = {{5, 6}, {7, 8}};\n'
            '    int result[N][N];\n'
            '    matrix_multiply(a, b, result);\n'
            '    for (int i = 0; i < N; i++) {\n'
            '        for (int j = 0; j < N; j++)\n'
            '            printf("%d ", result[i][j]);\n'
            '        printf("\\n");\n'
            '    }\n'
            '    return 0;\n'
            '}'
        ),
        "cpp": (
            '#include <iostream>\n'
            '#include <vector>\n\n'
            'using Matrix = std::vector<std::vector<int>>;\n\n'
            'Matrix multiply(const Matrix& a, const Matrix& b) {\n'
            '    int n = a.size(), m = b[0].size(), k = b.size();\n'
            '    Matrix result(n, std::vector<int>(m, 0));\n'
            '    for (int i = 0; i < n; i++)\n'
            '        for (int j = 0; j < m; j++)\n'
            '            for (int p = 0; p < k; p++)\n'
            '                result[i][j] += a[i][p] * b[p][j];\n'
            '    return result;\n'
            '}\n\n'
            'int main() {\n'
            '    Matrix a = {{1, 2}, {3, 4}};\n'
            '    Matrix b = {{5, 6}, {7, 8}};\n'
            '    auto result = multiply(a, b);\n'
            '    for (auto& row : result) {\n'
            '        for (int v : row) std::cout << v << " ";\n'
            '        std::cout << std::endl;\n'
            '    }\n'
            '    return 0;\n'
            '}'
        ),
        "java": (
            'public class MatrixMultiply {\n'
            '    public static int[][] multiply(int[][] a, int[][] b) {\n'
            '        int n = a.length, m = b[0].length, k = b.length;\n'
            '        int[][] result = new int[n][m];\n'
            '        for (int i = 0; i < n; i++)\n'
            '            for (int j = 0; j < m; j++)\n'
            '                for (int p = 0; p < k; p++)\n'
            '                    result[i][j] += a[i][p] * b[p][j];\n'
            '        return result;\n'
            '    }\n\n'
            '    public static void main(String[] args) {\n'
            '        int[][] a = {{1, 2}, {3, 4}};\n'
            '        int[][] b = {{5, 6}, {7, 8}};\n'
            '        int[][] result = multiply(a, b);\n'
            '        for (int[] row : result) {\n'
            '            for (int v : row) System.out.print(v + " ");\n'
            '            System.out.println();\n'
            '        }\n'
            '    }\n'
            '}'
        ),
    }
    return templates.get(lang, templates["python"])


# ── Pattern registry ─────────────────────────────────────────────────────────

PATTERNS: list[tuple[list[str], str, callable]] = [
    (["hello world", "hello", "first program"], "Hello World", _hello_world),
    (["factorial", "n!", "n factorial"], "Factorial", _factorial),
    (["fibonacci", "fib sequence", "fib number"], "Fibonacci", _fibonacci),
    (["bubble sort", "sort array", "sort list", "sorting"], "Bubble Sort", _bubble_sort),
    (["binary search", "search sorted", "search array"], "Binary Search", _binary_search),
    (["prime", "is prime", "prime number", "sieve"], "Prime Check", _prime_check),
    (["linked list", "singly linked", "node list"], "Linked List", _linked_list),
    (["stack", "push pop", "lifo"], "Stack", _stack),
    (["reverse string", "reverse a string", "string reverse"], "Reverse String", _reverse_string),
    (["palindrome", "is palindrome", "palindrome check"], "Palindrome Check", _palindrome),
    (["calculator", "simple calculator", "basic calculator", "add subtract multiply divide"], "Calculator", _calculator),
    (["file", "read file", "write file", "file handling", "file io"], "File I/O", _file_read_write),
    (["matrix", "matrix multiply", "matrix multiplication"], "Matrix Multiplication", _matrix_multiply),
]


# ── Public API ───────────────────────────────────────────────────────────────

def generate_code(prompt: str, language: str = "python") -> dict[str, object]:
    """
    Generate code from a natural language prompt.

    Returns a dict with:
      - code: the generated source code
      - pattern: the matched pattern name
      - language: target language
      - confidence: match confidence (0-100)
      - suggestions: list of alternative patterns the user might try
    """
    lang = language.lower() if language else "python"
    if lang not in {"python", "c", "cpp", "java"}:
        lang = "python"

    prompt_lower = prompt.lower().strip()

    # Score each pattern
    scored: list[tuple[int, str, callable]] = []
    for keywords, name, func in PATTERNS:
        score = _match_score(prompt_lower, keywords)
        if score > 0:
            scored.append((score, name, func))

    scored.sort(key=lambda x: x[0], reverse=True)

    if not scored:
        # Fallback: generate a hello world with a note
        return {
            "code": _hello_world(lang),
            "pattern": "Hello World (fallback)",
            "language": lang,
            "confidence": 20,
            "message": (
                "Could not match your prompt to a known pattern. "
                "Showing a Hello World template instead. "
                "Try prompts like: 'factorial', 'binary search', 'linked list', "
                "'bubble sort', 'fibonacci', 'prime check', 'stack', 'palindrome', "
                "'calculator', 'file handling', 'matrix multiplication', 'reverse string'."
            ),
            "suggestions": [name for _, name, _ in PATTERNS[:6]],
        }

    best_score, best_name, best_func = scored[0]
    max_possible = max(len(kws) for kws, _, _ in PATTERNS)
    confidence = min(100, int((best_score / max(max_possible, 1)) * 100) + 40)

    code = best_func(lang)
    suggestions = [name for _, name, _ in scored[1:4]] if len(scored) > 1 else []

    return {
        "code": code,
        "pattern": best_name,
        "language": lang,
        "confidence": confidence,
        "message": f"Generated {best_name} code in {lang}.",
        "suggestions": suggestions,
    }


def list_available_patterns() -> list[str]:
    """Return a list of all supported code generation pattern names."""
    return [name for _, name, _ in PATTERNS]
