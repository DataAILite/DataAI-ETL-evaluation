import React, { useContext } from 'react';
import ReactDOM from 'react-dom';
import {
  AyxAppWrapper,
  Box,
  Checkbox,
  Divider,
  FormControlLabel,
  Grid,
  TextField,
  Typography
} from '@alteryx/ui';
import { Context as UiSdkContext, DesignerApi } from '@alteryx/react-comms';


const defaultConfiguration = {
  sparkSubmit: 'spark-submit.cmd',
  master: 'local[*]',
  deployMode: 'client',
  sourceTable: '',
  cleanTable: '',
  rejectedTable: '',
  profileTable: '',
  findingsTable: '',
  normalize: true,
  recordKeyColumns: '',
  minimumQualityScore: '',
  rulesJson: '[]',
  extraSparkArgs: '[]',
  timeoutSeconds: '3600',
  evaluationAccepted: false
};


const App = () => {
  const [model, handleUpdateModel] = useContext(UiSdkContext);
  const configuration = { ...defaultConfiguration, ...(model.Configuration || {}) };

  const update = (name: string, value: any) => {
    handleUpdateModel({
      ...model,
      Configuration: {
        ...configuration,
        [name]: value
      }
    });
  };

  const field = (
    name: string,
    label: string,
    helperText: string,
    multiline = false
  ) => (
    <TextField
      fullWidth
      helperText={helperText}
      label={label}
      multiline={multiline}
      onChange={(event: any) => update(name, event.target.value)}
      rows={multiline ? 5 : undefined}
      value={configuration[name] || ''}
      variant="outlined"
    />
  );

  return (
    <Box p={3}>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Typography variant="h2">DataAI ETL Quality</Typography>
          <Typography variant="body2">
            Runs the embedded DataAI Spark ETL libraries in your Spark environment.
            No customer rows or credentials are sent to Yanbor LLC.
          </Typography>
        </Grid>

        <Grid item xs={12}><Divider /></Grid>
        <Grid item xs={12}><Typography variant="h3">Spark runtime</Typography></Grid>
        <Grid item xs={12}>
          {field('sparkSubmit', 'Spark Submit', 'Full path or command name for spark-submit.')}
        </Grid>
        <Grid item xs={8}>
          {field('master', 'Spark Master', 'Examples: local[*], yarn, spark://host:7077.')}
        </Grid>
        <Grid item xs={4}>
          <TextField
            fullWidth
            label="Deploy Mode"
            onChange={(event: any) => update('deployMode', event.target.value)}
            select
            SelectProps={{ native: true }}
            value={configuration.deployMode}
            variant="outlined"
          >
            <option value="client">client</option>
            <option value="cluster">cluster</option>
          </TextField>
        </Grid>

        <Grid item xs={12}><Typography variant="h3">Spark catalog tables</Typography></Grid>
        <Grid item xs={12}>
          {field('sourceTable', 'Source Table', 'Required. The source is read from the active Spark catalog.')}
        </Grid>
        <Grid item xs={6}>{field('cleanTable', 'Clean Table', 'Optional. Overwritten when specified.')}</Grid>
        <Grid item xs={6}>{field('rejectedTable', 'Rejected Table', 'Optional. Overwritten when specified.')}</Grid>
        <Grid item xs={6}>{field('profileTable', 'Profile Table', 'Optional. Overwritten when specified.')}</Grid>
        <Grid item xs={6}>{field('findingsTable', 'Findings Table', 'Optional. Overwritten when specified.')}</Grid>

        <Grid item xs={12}><Typography variant="h3">Quality controls</Typography></Grid>
        <Grid item xs={12}>
          <FormControlLabel
            control={
              <Checkbox
                checked={Boolean(configuration.normalize)}
                color="primary"
                onChange={(event: any) => update('normalize', event.target.checked)}
              />
            }
            label="Normalize strings before validation"
          />
        </Grid>
        <Grid item xs={6}>
          {field('recordKeyColumns', 'Record Key Columns', 'Optional comma-separated key column names.')}
        </Grid>
        <Grid item xs={6}>
          {field('minimumQualityScore', 'Minimum Quality Score', 'Optional value from 0 through 100.')}
        </Grid>
        <Grid item xs={12}>
          {field('rulesJson', 'Rules JSON', 'JSON array of DataAI RuleSpec objects.', true)}
        </Grid>

        <Grid item xs={12}><Typography variant="h3">Advanced</Typography></Grid>
        <Grid item xs={12}>
          {field('extraSparkArgs', 'Extra Spark Arguments', 'JSON string array; arguments are passed without a command shell.', true)}
        </Grid>
        <Grid item xs={12}>
          {field('timeoutSeconds', 'Timeout Seconds', 'From 1 through 86400. Default: 3600.')}
        </Grid>

        <Grid item xs={12}><Divider /></Grid>
        <Grid item xs={12}>
          <FormControlLabel
            control={
              <Checkbox
                checked={Boolean(configuration.evaluationAccepted)}
                color="primary"
                onChange={(event: any) => update('evaluationAccepted', event.target.checked)}
              />
            }
            label="I accept LICENSE.md for evaluation use and understand that output tables are overwritten when specified."
          />
        </Grid>
      </Grid>
    </Box>
  );
};


const Tool = () => (
  <DesignerApi messages={{}} defaultConfig={{ Configuration: defaultConfiguration }}>
    <AyxAppWrapper>
      <App />
    </AyxAppWrapper>
  </DesignerApi>
);


ReactDOM.render(<Tool />, document.getElementById('app'));
