
import React, { useState } from 'react';

import {
  Paper,
  Box,
  Grid,
  TextField,
  RadioGroup,
  FormControlLabel,
  Radio,
  FormControl,
  Typography,
  Select,
  MenuItem,
  Button,
} from '@mui/material';

// Function to sanitize and validate input (removes suspicious attributes and checks for invalid patterns)
const sanitizeAndValidateInput = (input) => {
  const unsafePattern = /<.*?>|on\w+=".*?"|alert|script/i; // Detects HTML, event handlers, and JavaScript keywords
  if (unsafePattern.test(input)) {
    return null; // Return null if input is malicious
  }
  return input.trim(); // Return sanitized and trimmed input
};

function PolicyForm({ policyCategory, onApply }) {
  const [formData, setFormData] = useState({
    SafeBrowsingProtectionLevel: '1',
    BlockObstructiveWebsites: 'not_configured',
    OverrideCertificateErrors: 'not_configured',
    BlockExcessiveAds: 'not_configured',
    BlockInjectedCode: 'not_configured',
    WhitelistExtensions: '',
    BlacklistExtensions: '',
    geolocation: 'allow',
    camera: 'allow',
    sensor: 'allow',
    notifications: 'allow',
    js: 'allow',
    popups: 'allow',
    usb: 'allow',
    BlockURLs: '',
    AllowURLs: '',
    block_all: 'no',
    data_type: 'browsing_history',
    time_to_live_in_hours: '1',
    PrintWebpage: 'not_configured',
    AutomaticBrowserSync: 'not_configured',
    SaveBrowserHistory: 'not_configured',
    Autofill: 'not_configured',
    CaptureScreenshots: 'not_configured',
    RememberPasswords: 'not_configured',
    SitePerProcess: 'not_configured',
    SearchSuggestions: 'not_configured',
    MetricsReporting: 'not_configured',
    PromptDownloadLocation: 'not_configured',
    BrowserHistoryDeletion: 'not_configured',
    BackgroundProcessing: 'not_configured',
    NetworkPredictions: 'not_configured',
    ThirdPartyCookies: 'not_configured',
  });

  const [error, setError] = useState(''); // State for error messages

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    const sanitizedValue = sanitizeAndValidateInput(value); // Sanitize and validate input

    if (sanitizedValue === null) {
      setError(`Invalid input detected in "${name}". Please correct it.`); // Show error
    } else {
      setError(''); // Clear error if input is valid
      setFormData((prevFormData) => ({
        ...prevFormData,
        [name]: sanitizedValue,
      }));
    }
  };


  const handleSubmit = (e) => {
    e.preventDefault();
    let filteredFormData = {};

  // Check if any input is invalid before submitting
    const hasInvalidInput = Object.values(formData).some(
        (value) => sanitizeAndValidateInput(value) === null
      );
    
      if (hasInvalidInput) {
        setError('Submission blocked: Invalid input detected.'); // Block submission
        return;
      }

    if (policyCategory === 'Threat Prevention') {
      filteredFormData = {
        SafeBrowsingProtectionLevel: formData.SafeBrowsingProtectionLevel,
        BlockObstructiveWebsites: formData.BlockObstructiveWebsites,
        OverrideCertificateErrors: formData.OverrideCertificateErrors,
        BlockExcessiveAds: formData.BlockExcessiveAds,
        BlockInjectedCode: formData.BlockInjectedCode,
        WhitelistExtensions: formData.WhitelistExtensions,
        BlacklistExtensions: formData.BlacklistExtensions,
        geolocation: formData.geolocation,
        camera: formData.camera,
        sensor: formData.sensor,
        notifications: formData.notifications,
        js: formData.js,
        popups: formData.popups,
        usb: formData.usb,
      };
    } else if (policyCategory === 'Data Leakage') {
      filteredFormData = {
        data_type: formData.data_type,
        time_to_live_in_hours: formData.time_to_live_in_hours,
        PrintWebpage: formData.PrintWebpage,
        AutomaticBrowserSync: formData.AutomaticBrowserSync,
        SaveBrowserHistory: formData.SaveBrowserHistory,
        Autofill: formData.Autofill,
        CaptureScreenshots: formData.CaptureScreenshots,
        RememberPasswords: formData.RememberPasswords,
        SitePerProcess: formData.SitePerProcess,
        SearchSuggestions: formData.SearchSuggestions,
        MetricsReporting: formData.MetricsReporting,
        PromptDownloadLocation: formData.PromptDownloadLocation,
        BrowserHistoryDeletion: formData.BrowserHistoryDeletion,
        BackgroundProcessing: formData.BackgroundProcessing,
        NetworkPredictions: formData.NetworkPredictions,
        ThirdPartyCookies: formData.ThirdPartyCookies,
        BlockURLs: formData.BlockURLs,
        AllowURLs: formData.AllowURLs,
      };
    }

    setError(''); // Clear error
    const finalConfigurations = {
      classification: policyCategory,
      ...filteredFormData,
    };

    onApply(finalConfigurations); // Pass form data to backend
  };

  return (
    <Paper elevation={3} sx={{ padding: 3, marginTop: 3 }}>
      <Typography variant="h5" gutterBottom>
        Configure Policies for {policyCategory}
      </Typography>
      <Box component="form" onSubmit={handleSubmit}>
        <Grid container spacing={3}>
          {/* Threat Prevention Fields */}
          {policyCategory === 'Threat Prevention' && (
            <>
              <Grid item xs={12}>
                <FormControl component="fieldset" fullWidth>
                  <Typography variant="subtitle1">Safe Browsing Protection Level</Typography>
                  <RadioGroup
                    name="SafeBrowsingProtectionLevel"
                    value={formData.SafeBrowsingProtectionLevel}
                    onChange={handleInputChange}
                  >
                    <FormControlLabel value="0" control={<Radio />} label="No Protection" />
                    <FormControlLabel value="1" control={<Radio />} label="Standard Protection" />
                    <FormControlLabel value="2" control={<Radio />} label="Enhanced Protection" />
                  </RadioGroup>
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <FormControl component="fieldset" fullWidth>
                  <Typography variant="subtitle1">Block Obstructive Websites</Typography>
                  <RadioGroup
                    name="BlockObstructiveWebsites"
                    value={formData.BlockObstructiveWebsites}
                    onChange={handleInputChange}
                  >
                    <FormControlLabel value="enable" control={<Radio />} label="Enable" />
                    <FormControlLabel value="disable" control={<Radio />} label="Disable" />
                    <FormControlLabel value="not_configured" control={<Radio />} label="Not Configured" />
                  </RadioGroup>
                </FormControl>
              </Grid>
              {/* Additional fields for Threat Prevention */}
                            {/* Override Certificate Errors */}
              <Grid item xs={12}>
                  <FormControl component="fieldset">
                    <Typography variant="subtitle1">Override Certificate Errors</Typography>
                    <RadioGroup
                      name="OverrideCertificateErrors"
                      value={formData.OverrideCertificateErrors}
                      onChange={handleInputChange}
                    >
                      <FormControlLabel value="enable" control={<Radio />} label="Enable" />
                      <FormControlLabel value="disable" control={<Radio />} label="Disable" />
                      <FormControlLabel value="not_configured" control={<Radio />} label="Not Configured" />
                    </RadioGroup>
                  </FormControl>
                </Grid>
                {/* Block Websites with Excessive Ads  */}
              <Grid item xs={12}>
                  <FormControl component="fieldset">
                    <Typography variant="subtitle1">Block Websites with Excessive Ads</Typography>
                    <RadioGroup
                      name="BlockExcessiveAds"
                      value={formData.BlockExcessiveAds}
                      onChange={handleInputChange}
                    >
                      <FormControlLabel value="enable" control={<Radio />} label="Enable" />
                      <FormControlLabel value="disable" control={<Radio />} label="Disable" />
                      <FormControlLabel value="not_configured" control={<Radio />} label="Not Configured" />
                    </RadioGroup>
                  </FormControl>
                </Grid>
                <Grid item xs={12}>
                  <FormControl component="fieldset">
                    <Typography variant="subtitle1">Block Third-Party Websites that Inject Code</Typography>
                    <RadioGroup
                      name="BlockInjectedCode"
                      value={formData.BlockInjectedCode}
                      onChange={handleInputChange}
                    >
                      <FormControlLabel value="enable" control={<Radio />} label="Enable" />
                      <FormControlLabel value="disable" control={<Radio />} label="Disable" />
                      <FormControlLabel value="not_configured" control={<Radio />} label="Not Configured" />
                    </RadioGroup>
                  </FormControl>
                </Grid>

                {/* Whitelist Extensions */}
                <Grid item xs={12}>
                  <TextField
                    label="Whitelist Extensions (comma-separated)"
                    name="WhitelistExtensions"
                    value={formData.WhitelistExtensions}
                    onChange={handleInputChange}
                    fullWidth
                    variant="outlined"
                  />
                </Grid>

                {/* Blacklist Extensions */}
                <Grid item xs={12}>
                  <TextField
                    label="Blacklist Extensions (comma-separated)"
                    name="BlacklistExtensions"
                    value={formData.BlacklistExtensions}
                    onChange={handleInputChange}
                    fullWidth
                    variant="outlined"
                  />
                </Grid>

                {/* Site Settings */}
                <Typography variant="h6">Site Settings</Typography>

                {/* Geolocation Access */}
                <Grid item xs={12}>
                  <FormControl component="fieldset">
                    <Typography variant="subtitle1">Geolocation Access</Typography>
                    <RadioGroup
                      name="geolocation"
                      value={formData.geolocation}
                      onChange={handleInputChange}
                    >
                      <FormControlLabel value="allow" control={<Radio />} label="Allow" />
                      <FormControlLabel value="block" control={<Radio />} label="Block" />
                    </RadioGroup>
                  </FormControl>
                </Grid>

                {/* Camera Access */}
                <Grid item xs={12}>
                  <FormControl component="fieldset">
                    <Typography variant="subtitle1">Camera Access</Typography>
                    <RadioGroup
                      name="camera"
                      value={formData.camera}
                      onChange={handleInputChange}
                    >
                      <FormControlLabel value="allow" control={<Radio />} label="Allow" />
                      <FormControlLabel value="block" control={<Radio />} label="Block" />
                    </RadioGroup>
                  </FormControl>
                </Grid>

                {/* Motion Sensors */}
                <Grid item xs={12}>
                  <FormControl component="fieldset">
                    <Typography variant="subtitle1">Motion Sensors</Typography>
                    <RadioGroup
                      name="sensor"
                      value={formData.sensor}
                      onChange={handleInputChange}
                    >
                      <FormControlLabel value="allow" control={<Radio />} label="Allow" />
                      <FormControlLabel value="block" control={<Radio />} label="Block" />
                    </RadioGroup>
                  </FormControl>
                </Grid>

                {/* Notifications */}
                <Grid item xs={12}>
                  <FormControl component="fieldset">
                    <Typography variant="subtitle1">Notifications</Typography>
                    <RadioGroup
                      name="notifications"
                      value={formData.notifications}
                      onChange={handleInputChange}
                    >
                      <FormControlLabel value="allow" control={<Radio />} label="Allow" />
                      <FormControlLabel value="block" control={<Radio />} label="Block" />
                    </RadioGroup>
                  </FormControl>
                </Grid>

                {/* JavaScript */}
                <Grid item xs={12}>
                  <FormControl component="fieldset">
                    <Typography variant="subtitle1">JavaScript</Typography>
                    <RadioGroup
                      name="js"
                      value={formData.js}
                      onChange={handleInputChange}
                    >
                      <FormControlLabel value="allow" control={<Radio />} label="Allow" />
                      <FormControlLabel value="block" control={<Radio />} label="Block" />
                    </RadioGroup>
                  </FormControl>
                </Grid>

                {/* Pop-ups */}
                <Grid item xs={12}>
                  <FormControl component="fieldset">
                    <Typography variant="subtitle1">Pop-ups</Typography>
                    <RadioGroup
                      name="popups"
                      value={formData.popups}
                      onChange={handleInputChange}
                    >
                      <FormControlLabel value="allow" control={<Radio />} label="Allow" />
                      <FormControlLabel value="block" control={<Radio />} label="Block" />
                    </RadioGroup>
                  </FormControl>
                </Grid>

                {/* Web USB Access */}
                <Grid item xs={12}>
                  <FormControl component="fieldset">
                    <Typography variant="subtitle1">Web USB Access</Typography>
                    <RadioGroup
                      name="usb"
                      value={formData.usb}
                      onChange={handleInputChange}
                    >
                      <FormControlLabel value="allow" control={<Radio />} label="Allow" />
                      <FormControlLabel value="block" control={<Radio />} label="Block" />
                    </RadioGroup>
                  </FormControl>
                </Grid>

                {/* Block URLs */}
                <Grid item xs={12}>
                  <TextField
                    label="Enter URLs to be blocked"
                    name="BlockURLs"
                    value={formData.BlockURLs}
                    onChange={handleInputChange}
                    fullWidth
                    variant="outlined"
                    placeholder="Enter URLs to be blocked"
                  />
                </Grid>

                {/* Allow URLs */}
                <Grid item xs={12}>
                  <TextField
                    label="Enter URLs to be allowed"
                    name="AllowURLs"
                    value={formData.AllowURLs}
                    onChange={handleInputChange}
                    fullWidth
                    variant="outlined"
                    placeholder="Enter URLs to be allowed"
                  />
                </Grid>
              
            </>
          )}

          {/* Data Leakage Fields */}
          {policyCategory === 'Data Leakage' && (
            <>
              <Grid item xs={12}>
                <FormControl component="fieldset" fullWidth>
                  <Typography variant="subtitle1">Print Webpage</Typography>
                  <RadioGroup
                    name="PrintWebpage"
                    value={formData.PrintWebpage}
                    onChange={handleInputChange}
                  >
                    <FormControlLabel value="allow" control={<Radio />} label="Allow" />
                    <FormControlLabel value="restrict" control={<Radio />} label="Restrict" />
                    <FormControlLabel value="not_configured" control={<Radio />} label="Not Configured" />
                  </RadioGroup>
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <FormControl component="fieldset" fullWidth>
                  <Typography variant="subtitle1">Automatic Browser Sync</Typography>
                  <RadioGroup
                    name="AutomaticBrowserSync"
                    value={formData.AutomaticBrowserSync}
                    onChange={handleInputChange}
                  >
                    <FormControlLabel value="allow" control={<Radio />} label="Allow" />
                    <FormControlLabel value="restrict" control={<Radio />} label="Restrict" />
                    <FormControlLabel value="not_configured" control={<Radio />} label="Not Configured" />
                  </RadioGroup>
                </FormControl>
              </Grid>
              {/* Additional fields for Data Leakage */}

                              {/* Save Browser History */}
                <Grid item xs={12}>
                  <FormControl component="fieldset">
                    <Typography variant="subtitle1">Save Browser History</Typography>
                    <RadioGroup
                      name="SaveBrowserHistory"
                      value={formData.SaveBrowserHistory}
                      onChange={handleInputChange}
                    >
                      <FormControlLabel value="allow" control={<Radio />} label="Allow" />
                      <FormControlLabel value="restrict" control={<Radio />} label="Restrict" />
                      <FormControlLabel value="not_configured" control={<Radio />} label="Not Configured" />
                    </RadioGroup>
                  </FormControl>
                </Grid>

                  {/* Autofill */}
                  <Grid item xs={12}>
                  <FormControl component="fieldset">
                    <Typography variant="subtitle1">Autofill</Typography>
                    <RadioGroup
                      name="Autofill"
                      value={formData.Autofill}
                      onChange={handleInputChange}
                    >
                      <FormControlLabel value="allow" control={<Radio />} label="Allow" />
                      <FormControlLabel value="restrict" control={<Radio />} label="Restrict" />
                      <FormControlLabel value="not_configured" control={<Radio />} label="Not Configured" />
                    </RadioGroup>
                  </FormControl>
                </Grid>
                
                                {/* Capture Screenshots */}
                                <Grid item xs={12}>
                  <FormControl component="fieldset">
                    <Typography variant="subtitle1">Capture Screenshots</Typography>
                    <RadioGroup
                      name="CaptureScreenshots"
                      value={formData.CaptureScreenshots}
                      onChange={handleInputChange}
                    >
                      <FormControlLabel value="allow" control={<Radio />} label="Allow" />
                      <FormControlLabel value="restrict" control={<Radio />} label="Restrict" />
                      <FormControlLabel value="not_configured" control={<Radio />} label="Not Configured" />
                    </RadioGroup>
                  </FormControl>
                </Grid>

                {/* Remember Passwords */}
                <Grid item xs={12}>
                  <FormControl component="fieldset">
                    <Typography variant="subtitle1">Remember Passwords</Typography>
                    <RadioGroup
                      name="RememberPasswords"
                      value={formData.RememberPasswords}
                      onChange={handleInputChange}
                    >
                      <FormControlLabel value="allow" control={<Radio />} label="Allow" />
                      <FormControlLabel value="restrict" control={<Radio />} label="Restrict" />
                      <FormControlLabel value="not_configured" control={<Radio />} label="Not Configured" />
                    </RadioGroup>
                  </FormControl>
                </Grid>

                {/* Site Per Process */}
                <Grid item xs={12}>
                  <FormControl component="fieldset">
                    <Typography variant="subtitle1">Site Per Process</Typography>
                    <RadioGroup
                      name="SitePerProcess"
                      value={formData.SitePerProcess}
                      onChange={handleInputChange}
                    >
                      <FormControlLabel value="enable" control={<Radio />} label="Enable" />
                      <FormControlLabel value="disable" control={<Radio />} label="Disable" />
                      <FormControlLabel value="not_configured" control={<Radio />} label="Not Configured" />
                    </RadioGroup>
                  </FormControl>
                </Grid>

                {/* Search Suggestions */}
                <Grid item xs={12}>
                  <FormControl component="fieldset">
                    <Typography variant="subtitle1">Search Suggestions</Typography>
                    <RadioGroup
                      name="SearchSuggestions"
                      value={formData.SearchSuggestions}
                      onChange={handleInputChange}
                    >
                      <FormControlLabel value="enable" control={<Radio />} label="Enable" />
                      <FormControlLabel value="disable" control={<Radio />} label="Disable" />
                      <FormControlLabel value="not_configured" control={<Radio />} label="Not Configured" />
                    </RadioGroup>
                  </FormControl>
                </Grid>

                {/* Metrics Reporting */}
                <Grid item xs={12}>
                  <FormControl component="fieldset">
                    <Typography variant="subtitle1">Metrics Reporting to Google</Typography>
                    <RadioGroup
                      name="MetricsReporting"
                      value={formData.MetricsReporting}
                      onChange={handleInputChange}
                    >
                      <FormControlLabel value="enable" control={<Radio />} label="Enable" />
                      <FormControlLabel value="disable" control={<Radio />} label="Disable" />
                      <FormControlLabel value="not_configured" control={<Radio />} label="Not Configured" />
                    </RadioGroup>
                  </FormControl>
                </Grid>

                {/* Prompt for Download Location */}
                <Grid item xs={12}>
                  <FormControl component="fieldset">
                    <Typography variant="subtitle1">Prompt for Download Location</Typography>
                    <RadioGroup
                      name="PromptDownloadLocation"
                      value={formData.PromptDownloadLocation}
                      onChange={handleInputChange}
                    >
                      <FormControlLabel value="enable" control={<Radio />} label="Enable" />
                      <FormControlLabel value="disable" control={<Radio />} label="Disable" />
                      <FormControlLabel value="not_configured" control={<Radio />} label="Not Configured" />
                    </RadioGroup>
                  </FormControl>
                </Grid>

                {/* Browser History Deletion */}
                <Grid item xs={12}>
                  <FormControl component="fieldset">
                    <Typography variant="subtitle1">Browser History Deletion</Typography>
                    <RadioGroup
                      name="BrowserHistoryDeletion"
                      value={formData.BrowserHistoryDeletion}
                      onChange={handleInputChange}
                    >
                      <FormControlLabel value="enable" control={<Radio />} label="Enable" />
                      <FormControlLabel value="disable" control={<Radio />} label="Disable" />
                      <FormControlLabel value="not_configured" control={<Radio />} label="Not Configured" />
                    </RadioGroup>
                  </FormControl>
                </Grid>

                {/* Background Processing */}
                <Grid item xs={12}>
                  <FormControl component="fieldset">
                    <Typography variant="subtitle1">Background Processing</Typography>
                    <RadioGroup
                      name="BackgroundProcessing"
                      value={formData.BackgroundProcessing}
                      onChange={handleInputChange}
                    >
                      <FormControlLabel value="enable" control={<Radio />} label="Enable" />
                      <FormControlLabel value="disable" control={<Radio />} label="Disable" />
                      <FormControlLabel value="not_configured" control={<Radio />} label="Not Configured" />
                    </RadioGroup>
                  </FormControl>
                </Grid>

                {/* Network Predictions */}
                <Grid item xs={12}>
                  <FormControl component="fieldset">
                    <Typography variant="subtitle1">Network Predictions</Typography>
                    <RadioGroup
                      name="NetworkPredictions"
                      value={formData.NetworkPredictions}
                      onChange={handleInputChange}
                    >
                      <FormControlLabel value="enable" control={<Radio />} label="Enable" />
                      <FormControlLabel value="disable" control={<Radio />} label="Disable" />
                      <FormControlLabel value="not_configured" control={<Radio />} label="Not Configured" />
                    </RadioGroup>
                  </FormControl>
                </Grid>

                {/* Third-Party Cookies */}
                <Grid item xs={12}>
                  <FormControl component="fieldset">
                    <Typography variant="subtitle1">Third-Party Cookies</Typography>
                    <RadioGroup
                      name="ThirdPartyCookies"
                      value={formData.ThirdPartyCookies}
                      onChange={handleInputChange}
                    >
                      <FormControlLabel value="always_allow" control={<Radio />} label="Always Allow" />
                      <FormControlLabel value="never_allow" control={<Radio />} label="Never Allow"/>
                      <FormControlLabel value="allow_visited_sites" control={<Radio />} label="Allow Only in Visited Sites" />
                      <FormControlLabel value="not_configured" control={<Radio />} label="Not Configured" />
                    </RadioGroup>
                  </FormControl>
                </Grid>

                {/* Configure Browsing Data Lifetime */}
                <Grid item xs={12}>
                  <FormControl component="fieldset">
                    <Typography variant="subtitle1">Configure Browsing Data Lifetime</Typography>
                    <span className="help-icon">(?)<span className="help-text">This allows admins to configure per data type when data is deleted by the browser. This is useful for working with sensitive customer data.</span></span>

                    {/* Select Data Type */}
                    <Typography variant="subtitle1">Select Data Type</Typography>
                    <Select
                      name="BrowsingDataLifetime[data_type]"
                      value={formData.data_type}
                      onChange={handleInputChange}
                      fullWidth
                      variant="outlined"
                    >
                      <MenuItem value="browsing_history">Browsing History</MenuItem>
                      <MenuItem value="download_history">Download History</MenuItem>
                      <MenuItem value="cookies_and_other_site_data">Cookies and Other Site Data</MenuItem>
                      <MenuItem value="cached_images_and_files">Cached Images and Files</MenuItem>
                      <MenuItem value="password_signin">Password Sign-in</MenuItem>
                      <MenuItem value="autofill">Autofill</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                {/* Time to Live */}
                  <Grid item xs={12}>
                  <TextField
                    label="Time to Live (in hours)"
                    name="BrowsingDataLifetime[time_to_live_in_hours]"
                    type="number"
                    value={formData.time_to_live_in_hours}
                    onChange={handleInputChange}
                    fullWidth
                    variant="outlined"
                    required
                    inputProps={{ min: "1" }}
                  />
                </Grid>

                                {/* Block URLs */}
                <Grid item xs={12}>
                  <TextField
                    label="Enter URLs to be blocked (comma-separated)"
                    name="BlockURLs"
                    value={formData.BlockURLs}
                    onChange={handleInputChange}
                    fullWidth
                    variant="outlined"
                    placeholder="Enter URLs to be blocked"
                  />
                </Grid>

                {/* Allow URLs */}
                <Grid item xs={12}>
                  <TextField
                    label="Enter URLs to be allowed (comma-separated)"
                    name="AllowURLs"
                    value={formData.AllowURLs}
                    onChange={handleInputChange}
                    fullWidth
                    variant="outlined"
                    placeholder="Enter URLs to be allowed"
                  />
                </Grid>
            </>
          )}

          <Grid item xs={12}>
            <Button
              variant="contained"
              color="primary"
              type="submit"
              sx={{ marginTop: 2, backgroundColor: '#0078D4' }}
            >
              Save and Apply
            </Button>
          </Grid>
        </Grid>
      </Box>
    </Paper>
  );
}

export default PolicyForm;
