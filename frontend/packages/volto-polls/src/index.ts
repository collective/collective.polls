import type { ConfigType } from '@plone/registry';
import installBlocks from './config/blocks';
import installComponents from './config/components';
import installReducers from './config/reducers';
import installSettings from './config/settings';
import installViews from './config/views';
import installWidgets from './config/widgets';

function applyConfig(config: ConfigType) {
  installSettings(config);
  installReducers(config);
  installComponents(config);
  installViews(config);
  installBlocks(config);
  installWidgets(config);

  return config;
}

export default applyConfig;
