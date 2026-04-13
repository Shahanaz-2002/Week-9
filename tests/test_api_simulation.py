import requests
import json
import time
import uuid

API_URL = "http://127.0.0.1:8000/analyze-case"


# =========================
# HELPER FUNCTIONS
# =========================

def print_divider():
    print("=" * 60)


def generate_patient_id():
    return f"P-{uuid.uuid4().hex[:6]}"


def add_patient_id(payload):
    payload["patient_id"] = generate_patient_id()
    return payload


# 🔹 SUCCESS RESPONSE VALIDATION
def validate_success_response(data):
    required_fields = [
        "status",
        "similar_cases",
        "predicted_diagnosis",
        "suggested_treatment",
        "confidence_score",
        "confidence_level",
        "clinical_explanation",
        "system_metrics"
    ]

    # Check fields exist
    for field in required_fields:
        if field not in data:
            return False, f"Missing field: {field}"

    # Type checks
    if data["status"] != "success":
        return False, "Status is not 'success'"

    if not isinstance(data["similar_cases"], list):
        return False, "similar_cases should be a list"

    if not (0.0 <= data["confidence_score"] <= 1.0):
        return False, "confidence_score out of range"

    if data["confidence_level"] not in ["Low", "Moderate", "High"]:
        return False, "Invalid confidence_level"

    if "response_time_ms" not in data["system_metrics"]:
        return False, "Missing system_metrics.response_time_ms"

    return True, "Valid response structure"


# 🔹 ERROR RESPONSE VALIDATION
def validate_error_response(data):
    if "detail" not in data:
        return False, "Missing 'detail' in error response"
    return True, "Valid error response"


def send_request(payload, test_name, expected_status):
    print_divider()
    print(f"TEST: {test_name}")

    payload = add_patient_id(payload)

    start_time = time.time()

    try:
        response = requests.post(API_URL, json=payload)
        response_time = round((time.time() - start_time) * 1000, 2)

        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {response_time} ms")

        try:
            data = response.json()
            print("Response JSON:")
            print(json.dumps(data, indent=4))
        except Exception:
            print("FAIL: Invalid JSON response")
            return False

        # 🔹 STATUS CHECK
        if response.status_code != expected_status:
            print(f"FAIL: Expected {expected_status}, got {response.status_code}")
            return False

        # 🔹 SUCCESS VALIDATION
        if response.status_code == 200:
            is_valid, message = validate_success_response(data)
            if not is_valid:
                print(f"FAIL: {message}")
                return False

        # 🔹 ERROR VALIDATION
        else:
            is_valid, message = validate_error_response(data)
            if not is_valid:
                print(f"FAIL: {message}")
                return False

        print("PASS")
        return True

    except Exception as e:
        print(f"ERROR: Request failed -> {e}")
        return False


# =========================
# TEST CASES
# =========================

test_cases = [

    # VALID CASE
    {
        "name": "Valid Case",
        "payload": {
            "symptoms": ["fever", "cough"],
            "age": 40,
            "gender": "male",
            "doctor_notes": "persistent for 2 days"
        },
        "expected_status": 200
    },

    # EMPTY SYMPTOMS
    {
        "name": "Empty Symptoms",
        "payload": {
            "symptoms": [],
            "age": 30,
            "gender": "female",
            "doctor_notes": ""
        },
        "expected_status": 422
    },

    # INVALID AGE
    {
        "name": "Invalid Age",
        "payload": {
            "symptoms": ["headache"],
            "age": -5,
            "gender": "male",
            "doctor_notes": ""
        },
        "expected_status": 422
    },

    # INVALID GENDER
    {
        "name": "Invalid Gender",
        "payload": {
            "symptoms": ["fatigue"],
            "age": 25,
            "gender": "unknown",
            "doctor_notes": ""
        },
        "expected_status": 422
    },

    # EMPTY STRINGS IN SYMPTOMS
    {
        "name": "Empty Symptom Values",
        "payload": {
            "symptoms": ["fever", ""],
            "age": 35,
            "gender": "female",
            "doctor_notes": ""
        },
        "expected_status": 422
    },

    # MISSING FIELD
    {
        "name": "Missing Symptoms Field",
        "payload": {
            "age": 50,
            "gender": "male"
        },
        "expected_status": 422
    },

    # LONG INPUT
    {
        "name": "Long Doctor Notes",
        "payload": {
            "symptoms": ["fever"],
            "age": 45,
            "gender": "male",
            "doctor_notes": "very long text " * 100
        },
        "expected_status": 200
    },

    # SINGLE SYMPTOM
    {
        "name": "Single Symptom",
        "payload": {
            "symptoms": ["cough"],
            "age": 28,
            "gender": "female",
            "doctor_notes": ""
        },
        "expected_status": 200
    }
]


# =========================
# MAIN EXECUTION
# =========================

if __name__ == "__main__":
    print("\nStarting CCMS Integration Simulation...\n")

    passed = 0
    failed = 0

    results_summary = []

    for test in test_cases:
        result = send_request(
            payload=test["payload"],
            test_name=test["name"],
            expected_status=test["expected_status"]
        )

        if result:
            passed += 1
            results_summary.append({"test": test["name"], "status": "PASS"})
        else:
            failed += 1
            results_summary.append({"test": test["name"], "status": "FAIL"})

    print_divider()
    print("FINAL SUMMARY")
    print(f"Total Tests: {len(test_cases)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    # SAVE RESULTS
    with open("test_results.json", "w") as f:
        json.dump(results_summary, f, indent=4)

    print("\nResults saved to test_results.json")
    print("CCMS Simulation Completed!")