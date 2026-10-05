import type { ConfigType } from '@plone/registry';
import PollOptionsWidget from '../components/Widgets/PollOptionsWidget/PollOptionsWidget';

/**
 * The widget the backend asks for on a poll's `options` field, through
 * `widget="poll_options"` on the `JSONField`.
 */
export const OPTIONS_WIDGET = 'poll_options';

/**
 * Register the poll options widget.
 *
 * @param config - The Volto configuration registry.
 * @returns The same registry.
 */
export default function install(config: ConfigType) {
  config.widgets.widget[OPTIONS_WIDGET] = PollOptionsWidget;
  return config;
}
