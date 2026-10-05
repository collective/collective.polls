/**
 * A Redux store stand-in for tests: a fixed state, and a record of every
 * action dispatched. It runs no reducers and no middleware.
 */
export interface RecordingStore {
  getState: () => Record<string, unknown>;
  subscribe: () => () => void;
  dispatch: (action: any) => any;
  /** Every action dispatched so far, in order. */
  actions: any[];
}

/**
 * Build a recording store.
 *
 * @param state The state every `getState` returns.
 * @param dispatch What `dispatch` returns for an action; the action itself
 *   by default.
 */
export function recordingStore(
  state: Record<string, unknown>,
  dispatch: (action: any) => any = (action) => action,
): RecordingStore {
  const actions: any[] = [];
  return {
    getState: () => state,
    subscribe: () => () => undefined,
    dispatch: (action) => {
      actions.push(action);
      return dispatch(action);
    },
    actions,
  };
}
