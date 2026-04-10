import { useState, useCallback, useEffect } from "react";
import { fetchBillingStatus, createCheckoutSession } from "../api.js";

export function useBilling(sessionToken) {
  const [billingStatus, setBillingStatus] = useState(null);
  const [paywallVisible, setPaywallVisible] = useState(false);
  const [checkoutLoading, setCheckoutLoading] = useState(false);

  useEffect(() => {
    if (!sessionToken) {
      setBillingStatus(null);
      return;
    }
    fetchBillingStatus(sessionToken)
      .then(setBillingStatus)
      .catch(() => setBillingStatus(null));
  }, [sessionToken]);

  const refreshBilling = useCallback(() => {
    if (!sessionToken) return;
    fetchBillingStatus(sessionToken)
      .then(setBillingStatus)
      .catch(() => {});
  }, [sessionToken]);

  const checkScanAllowed = useCallback(() => {
    if (!billingStatus) return true;
    if (billingStatus.scans_remaining === null) return true;
    if (billingStatus.scans_remaining > 0) return true;
    setPaywallVisible(true);
    return false;
  }, [billingStatus]);

  const openCheckout = useCallback(async (plan, billing = "monthly") => {
    if (!sessionToken) return;
    setCheckoutLoading(true);
    try {
      const { url } = await createCheckoutSession(plan, billing, sessionToken);
      if (url) window.location.href = url;
    } catch (err) {
      console.error("Checkout failed:", err);
    } finally {
      setCheckoutLoading(false);
    }
  }, [sessionToken]);

  const dismissPaywall = useCallback(() => setPaywallVisible(false), []);

  return {
    billingStatus,
    paywallVisible,
    checkoutLoading,
    checkScanAllowed,
    openCheckout,
    dismissPaywall,
    refreshBilling,
  };
}
