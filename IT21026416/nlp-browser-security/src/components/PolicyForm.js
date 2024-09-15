import React, { useState} from "react";

function PolicyForm({ policyCategory, onApply }) {
  const [formData, setFormData] = useState({
    SafeBrowsingProtectionLevel: "1",
    BlockObstructiveWebsites: "not_configured",
    OverrideCertificateErrors: "not_configured",
    BlockExcessiveAds: "not_configured",
    BlockInjectedCode: "not_configured",
    WhitelistExtensions: "",
    BlacklistExtensions: "",
    geolocation: "allow",
    camera: "allow",
    sensor: "allow",
    notifications: "allow",
    js: "allow",
    popups: "allow",
    usb: "allow",
    BlockURLs: "",
    AllowURLs: "",
    block_all: "no",
    data_type: "browsing_history",
    time_to_live_in_hours: "1",
    PrintWebpage: "not_configured",
    AutomaticBrowserSync: "not_configured",
    SaveBrowserHistory: "not_configured",
    Autofill: "not_configured",
    CaptureScreenshots: "not_configured",
    RememberPasswords: "not_configured",
    SitePerProcess: "not_configured",
    SearchSuggestions: "not_configured",
    MetricsReporting: "not_configured",
    PromptDownloadLocation: "not_configured",
    BrowserHistoryDeletion: "not_configured",
    BackgroundProcessing: "not_configured",
    NetworkPredictions: "not_configured",
    ThirdPartyCookies: "not_configured",
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevFormData) => ({
      ...prevFormData,
      [name]: value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const finalConfigurations = {
      classification: policyCategory, // Pass the classification here
      ...formData,
    };
    onApply(finalConfigurations); // Pass form data to App.js for backend submission
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Configure Policies for {policyCategory}</h2>

      {/* Safe Browsing Protection Level */}
      {policyCategory === "Threat Prevention" && (
        <>
          <label>Safe Browsing Protection Level</label>
          <div>
            <input
              type="radio"
              name="SafeBrowsingProtectionLevel"
              value="0"
              checked={formData.SafeBrowsingProtectionLevel === "0"}
              onChange={handleInputChange}
            /> No Protection
            <input
              type="radio"
              name="SafeBrowsingProtectionLevel"
              value="1"
              checked={formData.SafeBrowsingProtectionLevel === "1"}
              onChange={handleInputChange}
            /> Standard Protection
            <input
              type="radio"
              name="SafeBrowsingProtectionLevel"
              value="2"
              checked={formData.SafeBrowsingProtectionLevel === "2"}
              onChange={handleInputChange}
            /> Enhanced Protection
          </div>
                {/* Block Obstructive Websites */}
          <label>Block Obstructive Websites</label>
          <div>
            <input
              type="radio"
              name="BlockObstructiveWebsites"
              value="enable"
              checked={formData.BlockObstructiveWebsites === "enable"}
              onChange={handleInputChange}
            /> Enable
            <input
              type="radio"
              name="BlockObstructiveWebsites"
              value="disable"
              checked={formData.BlockObstructiveWebsites === "disable"}
              onChange={handleInputChange}
            /> Disable
            <input
              type="radio"
              name="BlockObstructiveWebsites"
              value="not_configured"
              checked={formData.BlockObstructiveWebsites === "not_configured"}
              onChange={handleInputChange}
            /> Not Configured
          </div>
        
            {/* Override Certificate Errors */}
          <label>Override Certificate Errors</label>
          <div>
            <input
              type="radio"
              name="OverrideCertificateErrors"
              value="enable"
              checked={formData.OverrideCertificateErrors === "enable"}
              onChange={handleInputChange}
            /> Enable
            <input
              type="radio"
              name="OverrideCertificateErrors"
              value="disable"
              checked={formData.OverrideCertificateErrors === "disable"}
              onChange={handleInputChange}
            /> Disable
            <input
              type="radio"
              name="OverrideCertificateErrors"
              value="not_configured"
              checked={formData.OverrideCertificateErrors === "not_configured"}
              onChange={handleInputChange}
            /> Not Configured
          </div>

          {/* Block Websites with Excessive Ads */}
          <label>Block Websites with Excessive Ads</label>
          <div>
            <input
              type="radio"
              name="BlockExcessiveAds"
              value="enable"
              checked={formData.BlockExcessiveAds === "enable"}
              onChange={handleInputChange}
            /> Enable
            <input
              type="radio"
              name="BlockExcessiveAds"
              value="disable"
              checked={formData.BlockExcessiveAds === "disable"}
              onChange={handleInputChange}
            /> Disable
            <input
              type="radio"
              name="BlockExcessiveAds"
              value="not_configured"
              checked={formData.BlockExcessiveAds === "not_configured"}
              onChange={handleInputChange}
            /> Not Configured
          </div>

          {/* Block Injected Code */}
          <label>Block Third-Party Websites that Inject Code</label>
          <div>
            <input
              type="radio"
              name="BlockInjectedCode"
              value="enable"
              checked={formData.BlockInjectedCode === "enable"}
              onChange={handleInputChange}
            /> Enable
            <input
              type="radio"
              name="BlockInjectedCode"
              value="disable"
              checked={formData.BlockInjectedCode === "disable"}
              onChange={handleInputChange}
            /> Disable
            <input
              type="radio"
              name="BlockInjectedCode"
              value="not_configured"
              checked={formData.BlockInjectedCode === "not_configured"}
              onChange={handleInputChange}
            /> Not Configured
          </div>

          {/* Whitelist Extensions */}
          <label>Whitelist Extensions (comma-separated)</label>
          <div>
            <input
              type="text"
              name="WhitelistExtensions"
              value={formData.WhitelistExtensions}
              onChange={handleInputChange}
            />
          </div>
          {/* Blacklist Extensions */}
          <label>Blacklist Extensions (comma-separated)</label>
          <div>

          
          <input
            type="text"
            name="BlacklistExtensions"
            value={formData.BlacklistExtensions}
            onChange={handleInputChange}
          />
          </div>
        </>
      )}

      {/* Block Obstructive Websites */}
      {policyCategory === "Data Leakage" && (
        <>
          <label>Print Webpage</label>
          <div>
            <input
              type="radio"
              name="PrintWebpage"
              value="allow"
              checked={formData.PrintWebpage === "allow"}
              onChange={handleInputChange}
            /> Allow
            <input
              type="radio"
              name="PrintWebpage"
              value="restrict"
              checked={formData.PrintWebpage === "restrict"}
              onChange={handleInputChange}
            /> Restrict
            <input
              type="radio"
              name="PrintWebpage"
              value="not_configured"
              checked={formData.PrintWebpage === "not_configured"}
              onChange={handleInputChange}
            /> Not Configured
          </div>

          {/* Automatic Browser Sync */}
          <label>Automatic Browser Sync</label>
          <div>
            <input
              type="radio"
              name="AutomaticBrowserSync"
              value="allow"
              checked={formData.AutomaticBrowserSync === "allow"}
              onChange={handleInputChange}
            /> Allow
            <input
              type="radio"
              name="AutomaticBrowserSync"
              value="restrict"
              checked={formData.AutomaticBrowserSync === "restrict"}
              onChange={handleInputChange}
            /> Restrict
            <input
              type="radio"
              name="AutomaticBrowserSync"
              value="not_configured"
              checked={formData.AutomaticBrowserSync === "not_configured"}
              onChange={handleInputChange}
            /> Not Configured
          </div>

          {/* Save Browser History */}
          <label>Save Browser History</label>
          <div>
            <input
              type="radio"
              name="SaveBrowserHistory"
              value="allow"
              checked={formData.SaveBrowserHistory === "allow"}
              onChange={handleInputChange}
            /> Allow
            <input
              type="radio"
              name="SaveBrowserHistory"
              value="restrict"
              checked={formData.SaveBrowserHistory === "restrict"}
              onChange={handleInputChange}
            /> Restrict
            <input
              type="radio"
              name="SaveBrowserHistory"
              value="not_configured"
              checked={formData.SaveBrowserHistory === "not_configured"}
              onChange={handleInputChange}
            /> Not Configured
          </div>

          {/* Autofill */}
          <label>Autofill</label>
          <div>
            <input
              type="radio"
              name="Autofill"
              value="allow"
              checked={formData.Autofill === "allow"}
              onChange={handleInputChange}
            /> Allow
            <input
              type="radio"
              name="Autofill"
              value="restrict"
              checked={formData.Autofill === "restrict"}
              onChange={handleInputChange}
            /> Restrict
            <input
              type="radio"
              name="Autofill"
              value="not_configured"
              checked={formData.Autofill === "not_configured"}
              onChange={handleInputChange}
            /> Not Configured
          </div>

          {/* Capture Screenshots */}
          <label>Capture Screenshots</label>
          <div>
            <input
              type="radio"
              name="CaptureScreenshots"
              value="allow"
              checked={formData.CaptureScreenshots === "allow"}
              onChange={handleInputChange}
            /> Allow
            <input
              type="radio"
              name="CaptureScreenshots"
              value="restrict"
              checked={formData.CaptureScreenshots === "restrict"}
              onChange={handleInputChange}
            /> Restrict
            <input
              type="radio"
              name="CaptureScreenshots"
              value="not_configured"
              checked={formData.CaptureScreenshots === "not_configured"}
              onChange={handleInputChange}
            /> Not Configured
          </div>

          {/* Remember Passwords */}
          <label>Remember Passwords</label>
          <div>
            <input
              type="radio"
              name="RememberPasswords"
              value="allow"
              checked={formData.RememberPasswords === "allow"}
              onChange={handleInputChange}
            /> Allow
            <input
              type="radio"
              name="RememberPasswords"
              value="restrict"
              checked={formData.RememberPasswords === "restrict"}
              onChange={handleInputChange}
            /> Restrict
            <input
              type="radio"
              name="RememberPasswords"
              value="not_configured"
              checked={formData.RememberPasswords === "not_configured"}
              onChange={handleInputChange}
            /> Not Configured
          </div>

          {/* Site Per Process */}
          <label>Site Per Process</label>
          <div>
            <input
              type="radio"
              name="SitePerProcess"
              value="enable"
              checked={formData.SitePerProcess === "enable"}
              onChange={handleInputChange}
            /> Enable
            <input
              type="radio"
              name="SitePerProcess"
              value="disable"
              checked={formData.SitePerProcess === "disable"}
              onChange={handleInputChange}
            /> Disable
            <input
              type="radio"
              name="SitePerProcess"
              value="not_configured"
              checked={formData.SitePerProcess === "not_configured"}
              onChange={handleInputChange}
            /> Not Configured
          </div>
          <label>Search Suggestions</label>
          <div>
            <input
              type="radio"
              name="SearchSuggestions"
              value="enable"
              checked={formData.SearchSuggestions === "enable"}
              onChange={handleInputChange}
            /> Enable
            <input
              type="radio"
              name="SearchSuggestions"
              value="disable"
              checked={formData.SearchSuggestions === "disable"}
              onChange={handleInputChange}
            /> Disable
            <input
              type="radio"
              name="SearchSuggestions"
              value="not_configured"
              checked={formData.SearchSuggestions === "not_configured"}
              onChange={handleInputChange}
            /> Not Configured
          </div>

          {/* Metrics Reporting */}
          <label>Metrics Reporting to Google</label>
          <div>
            <input
              type="radio"
              name="MetricsReporting"
              value="enable"
              checked={formData.MetricsReporting === "enable"}
              onChange={handleInputChange}
            /> Enable
            <input
              type="radio"
              name="MetricsReporting"
              value="disable"
              checked={formData.MetricsReporting === "disable"}
              onChange={handleInputChange}
            /> Disable
            <input
              type="radio"
              name="MetricsReporting"
              value="not_configured"
              checked={formData.MetricsReporting === "not_configured"}
              onChange={handleInputChange}
            /> Not Configured
          </div>

          {/* Prompt Download Location */}
          <label>Prompt for Download Location</label>
          <div>
            <input
              type="radio"
              name="PromptDownloadLocation"
              value="enable"
              checked={formData.PromptDownloadLocation === "enable"}
              onChange={handleInputChange}
            /> Enable
            <input
              type="radio"
              name="PromptDownloadLocation"
              value="disable"
              checked={formData.PromptDownloadLocation === "disable"}
              onChange={handleInputChange}
            /> Disable
            <input
              type="radio"
              name="PromptDownloadLocation"
              value="not_configured"
              checked={formData.PromptDownloadLocation === "not_configured"}
              onChange={handleInputChange}
            /> Not Configured
          </div>

          {/* Browser History Deletion */}
          <label>Browser History Deletion</label>
          <div>
            <input
              type="radio"
              name="BrowserHistoryDeletion"
              value="enable"
              checked={formData.BrowserHistoryDeletion === "enable"}
              onChange={handleInputChange}
            /> Enable
            <input
              type="radio"
              name="BrowserHistoryDeletion"
              value="disable"
              checked={formData.BrowserHistoryDeletion === "disable"}
              onChange={handleInputChange}
            /> Disable
            <input
              type="radio"
              name="BrowserHistoryDeletion"
              value="not_configured"
              checked={formData.BrowserHistoryDeletion === "not_configured"}
              onChange={handleInputChange}
            /> Not Configured
          </div>

          {/* Background Processing */}
          <label>Background Processing</label>
          <div>
            <input
              type="radio"
              name="BackgroundProcessing"
              value="enable"
              checked={formData.BackgroundProcessing === "enable"}
              onChange={handleInputChange}
            /> Enable
            <input
              type="radio"
              name="BackgroundProcessing"
              value="disable"
              checked={formData.BackgroundProcessing === "disable"}
              onChange={handleInputChange}
            /> Disable
            <input
              type="radio"
              name="BackgroundProcessing"
              value="not_configured"
              checked={formData.BackgroundProcessing === "not_configured"}
              onChange={handleInputChange}
            /> Not Configured
          </div>

          {/* Network Predictions */}
          <label>Network Predictions</label>
          <div>
            <input
              type="radio"
              name="NetworkPredictions"
              value="enable"
              checked={formData.NetworkPredictions === "enable"}
              onChange={handleInputChange}
            /> Enable
            <input
              type="radio"
              name="NetworkPredictions"
              value="disable"
              checked={formData.NetworkPredictions === "disable"}
              onChange={handleInputChange}
            /> Disable
            <input
              type="radio"
              name="NetworkPredictions"
              value="not_configured"
              checked={formData.NetworkPredictions === "not_configured"}
              onChange={handleInputChange}
            /> Not Configured
          </div>

          {/* Third-Party Cookies */}
          <label>Third-Party Cookies</label>
          <div>
            <input
              type="radio"
              name="ThirdPartyCookies"
              value="always_allow"
              checked={formData.ThirdPartyCookies === "always_allow"}
              onChange={handleInputChange}
            /> Always Allow
            <input
              type="radio"
              name="ThirdPartyCookies"
              value="never_allow"
              checked={formData.ThirdPartyCookies === "never_allow"}
              onChange={handleInputChange}
            /> Never Allow
            <input
              type="radio"
              name="ThirdPartyCookies"
              value="allow_visited_sites"
              checked={formData.ThirdPartyCookies === "allow_visited_sites"}
              onChange={handleInputChange}
            /> Allow Only in Visited Sites
            <input
              type="radio"
              name="ThirdPartyCookies"
              value="not_configured"
              checked={formData.ThirdPartyCookies === "not_configured"}
              onChange={handleInputChange}
            /> Not Configured
          </div>

        </>
      )}

      {/* Common for all categories */}
      <div>
        <label>Block URLs (comma-separated)</label>
        <input
          type="text"
          name="BlockURLs"
          value={formData.BlockURLs}
          onChange={handleInputChange}
          placeholder="Enter URLs to be blocked"
        />
      </div>

      <div>
        <label>Allow URLs (comma-separated)</label>
        <input
          type="text"
          name="AllowURLs"
          value={formData.AllowURLs}
          onChange={handleInputChange}
          placeholder="Enter URLs to be allowed"
        />        
      </div>


      {/* Submit Button */}
      <button type="submit">Save and Apply</button>
    </form>
  );
}

export default PolicyForm;
