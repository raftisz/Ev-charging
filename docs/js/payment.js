requireAuth();
renderSidebar("charging");

let sessionAmount = 0;
let selectedMethod = "credit_card";

document.querySelectorAll(".pay-method").forEach((el) => {
  el.addEventListener("click", () => {
    document.querySelectorAll(".pay-method").forEach((m) => m.classList.remove("selected"));
    el.classList.add("selected");
    el.querySelector("input").checked = true;
    selectedMethod = el.dataset.method;

    document.getElementById("card-fields").style.display = selectedMethod === "credit_card" ? "block" : "none";
    document.getElementById("promptpay-fields").style.display = selectedMethod === "promptpay" ? "block" : "none";
  });
});

function updateSummary() {
  document.getElementById("summary-amount").textContent = `฿${sessionAmount.toFixed(2)}`;
  document.getElementById("summary-total").textContent = `฿${sessionAmount.toFixed(2)}`;
}

document.getElementById("confirm-payment-btn").addEventListener("click", async () => {
  const btn = document.getElementById("confirm-payment-btn");
  btn.disabled = true;
  btn.textContent = "Processing...";

  try {
    await Api.post("/payments", { amount: sessionAmount, method: selectedMethod });
    showToast("Payment successful!");
    setTimeout(() => (window.location.href = "/pages/history.html"), 900);
  } catch (err) {
    showToast(err.message, true);
    btn.disabled = false;
    btn.textContent = "Confirm Payment";
  }
});

(async function init() {
  try {
    const [profile, session] = await Promise.all([
      Api.get("/profile"),
      Api.get("/charging/status").catch(() => null),
    ]);
    document.getElementById("wallet-balance-label").textContent = `Balance: ฿${profile.wallet_balance.toFixed(2)}`;
    sessionAmount = session ? session.current_cost || 150 : 150;
    updateSummary();
  } catch (err) {
    showToast(err.message, true);
  }
})();
