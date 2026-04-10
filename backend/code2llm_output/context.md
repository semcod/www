# System Architecture Analysis

## Overview

- **Project**: /tmp/semcod-sandbox-84fud4l9/repo
- **Primary Language**: ruby
- **Languages**: ruby: 34259, javascript: 10085, go: 160, shell: 39, typescript: 10
- **Analysis Mode**: static
- **Total Functions**: 131162
- **Total Classes**: 13902
- **Modules**: 44557
- **Entry Points**: 118116

## Architecture by Module

### app.models.project
- **Functions**: 441
- **Classes**: 1
- **File**: `project.rb`

### app.models.user
- **Functions**: 330
- **Classes**: 1
- **File**: `user.rb`

### app.models.merge_request
- **Functions**: 308
- **Classes**: 1
- **File**: `merge_request.rb`

### app.assets.javascripts.gfm_auto_complete
- **Functions**: 199
- **Classes**: 1
- **File**: `gfm_auto_complete.js`

### app.models.ci.pipeline
- **Functions**: 186
- **Classes**: 1
- **File**: `pipeline.rb`

### ee.app.models.ee.project
- **Functions**: 185
- **File**: `project.rb`

### app.models.repository
- **Functions**: 172
- **Classes**: 1
- **File**: `repository.rb`

### app.models.group
- **Functions**: 153
- **Classes**: 1
- **File**: `group.rb`

### app.assets.javascripts.deprecated_notes
- **Functions**: 149
- **Classes**: 1
- **File**: `deprecated_notes.js`

### scripts.frontend.infection_scanner.infection_scanner
- **Functions**: 143
- **File**: `infection_scanner.mjs`

### qa.qa.runtime.env
- **Functions**: 143
- **File**: `env.rb`

### ee.spec.frontend.work_items.components.work_item_types_list_spec
- **Functions**: 143
- **File**: `work_item_types_list_spec.js`

### app.assets.javascripts.diffs.stores.legacy_diffs.actions
- **Functions**: 137
- **File**: `actions.js`

### ee.app.models.ee.group
- **Functions**: 134
- **File**: `group.rb`

### app.assets.javascripts.diffs.store.actions
- **Functions**: 131
- **File**: `actions.js`

### ee.spec.frontend.ai.duo_agentic_chat.components.duo_agentic_chat_spec
- **Functions**: 127
- **File**: `duo_agentic_chat_spec.js`

### app.assets.javascripts.work_items.list.utils
- **Functions**: 125
- **File**: `utils.js`

### app.assets.javascripts.filtered_search.filtered_search_manager
- **Functions**: 119
- **Classes**: 1
- **File**: `filtered_search_manager.js`

### ee.app.models.ee.namespace
- **Functions**: 116
- **File**: `namespace.rb`

### app.models.namespace
- **Functions**: 115
- **Classes**: 1
- **File**: `namespace.rb`

## Key Entry Points

Main execution flows into the system:

### public.-.speedscope.speedscope.026f36b0.process
- **Calls**: public.-.speedscope.speedscope.026f36b0.defineProperty, public.-.speedscope.speedscope.026f36b0.Error, public.-.speedscope.speedscope.026f36b0.indexOf, public.-.speedscope.speedscope.026f36b0.push, public.-.speedscope.speedscope.026f36b0.splice, public.-.speedscope.speedscope.026f36b0.i, public.-.speedscope.speedscope.026f36b0.constructor, public.-.speedscope.speedscope.026f36b0.set

### app.assets.javascripts.api.DEFAULT_PER_PAGE
- **Calls**: app.assets.javascripts.api.group, app.assets.javascripts.api.buildUrl, app.assets.javascripts.api.replace, app.assets.javascripts.api.get, app.assets.javascripts.api.then, app.assets.javascripts.api.callback, app.assets.javascripts.api.groupPackages, app.assets.javascripts.api.projectPackages

### spec.frontend.ci.artifacts.components.job_artifacts_table_spec.jobArtifactsCountLimit
- **Calls**: spec.frontend.ci.artifacts.components.job_artifacts_table_spec.describe, spec.frontend.ci.artifacts.components.job_artifacts_table_spec.fn, spec.frontend.ci.artifacts.components.job_artifacts_table_spec.findComponent, spec.frontend.ci.artifacts.components.job_artifacts_table_spec.findAllComponents, spec.frontend.ci.artifacts.components.job_artifacts_table_spec.findTable, spec.frontend.ci.artifacts.components.job_artifacts_table_spec.findAll, spec.frontend.ci.artifacts.components.job_artifacts_table_spec.at, spec.frontend.ci.artifacts.components.job_artifacts_table_spec.findByTestId

### public.-.speedscope.import.e3a73ef4.t
- **Calls**: public.-.speedscope.import.e3a73ef4.Uint8Array, public.-.speedscope.import.e3a73ef4.foo, public.-.speedscope.import.e3a73ef4.subarray, public.-.speedscope.import.e3a73ef4.o, public.-.speedscope.import.e3a73ef4.RangeError, public.-.speedscope.import.e3a73ef4.f, public.-.speedscope.import.e3a73ef4.Error, public.-.speedscope.import.e3a73ef4.c

### app.assets.javascripts.users_select.UsersSelect
- **Calls**: app.assets.javascripts.users_select.toString, app.assets.javascripts.users_select.match, app.assets.javascripts.users_select.bind, app.assets.javascripts.users_select.parse, app.assets.javascripts.users_select.map, app.assets.javascripts.users_select.data, app.assets.javascripts.users_select.closest, app.assets.javascripts.users_select.next

### ee.app.assets.javascripts.orbit.utils.three_graph.CONNECTIONS_RENDER_ORDER
- **Calls**: ee.app.assets.javascripts.orbit.utils.three_graph.constructor, ee.app.assets.javascripts.orbit.utils.three_graph.GraphScene, ee.app.assets.javascripts.orbit.utils.three_graph.ThreeGraph.init, ee.app.assets.javascripts.orbit.utils.three_graph.Group, ee.app.assets.javascripts.orbit.utils.three_graph.add, ee.app.assets.javascripts.orbit.utils.three_graph.ThreeGraph.createGlobe, ee.app.assets.javascripts.orbit.utils.three_graph.ThreeGraph.createCityLights, ee.app.assets.javascripts.orbit.utils.three_graph.GraphInteraction

### ee.app.assets.javascripts.orbit.utils.three_graph.IMPULSES_RENDER_ORDER
- **Calls**: ee.app.assets.javascripts.orbit.utils.three_graph.constructor, ee.app.assets.javascripts.orbit.utils.three_graph.GraphScene, ee.app.assets.javascripts.orbit.utils.three_graph.ThreeGraph.init, ee.app.assets.javascripts.orbit.utils.three_graph.Group, ee.app.assets.javascripts.orbit.utils.three_graph.add, ee.app.assets.javascripts.orbit.utils.three_graph.ThreeGraph.createGlobe, ee.app.assets.javascripts.orbit.utils.three_graph.ThreeGraph.createCityLights, ee.app.assets.javascripts.orbit.utils.three_graph.GraphInteraction

### ee.app.assets.javascripts.orbit.utils.three_graph.EDGE_LABELS_RENDER_ORDER
- **Calls**: ee.app.assets.javascripts.orbit.utils.three_graph.constructor, ee.app.assets.javascripts.orbit.utils.three_graph.GraphScene, ee.app.assets.javascripts.orbit.utils.three_graph.ThreeGraph.init, ee.app.assets.javascripts.orbit.utils.three_graph.Group, ee.app.assets.javascripts.orbit.utils.three_graph.add, ee.app.assets.javascripts.orbit.utils.three_graph.ThreeGraph.createGlobe, ee.app.assets.javascripts.orbit.utils.three_graph.ThreeGraph.createCityLights, ee.app.assets.javascripts.orbit.utils.three_graph.GraphInteraction

### ee.app.assets.javascripts.orbit.utils.three_graph.NODE_LABELS_RENDER_ORDER
- **Calls**: ee.app.assets.javascripts.orbit.utils.three_graph.constructor, ee.app.assets.javascripts.orbit.utils.three_graph.GraphScene, ee.app.assets.javascripts.orbit.utils.three_graph.ThreeGraph.init, ee.app.assets.javascripts.orbit.utils.three_graph.Group, ee.app.assets.javascripts.orbit.utils.three_graph.add, ee.app.assets.javascripts.orbit.utils.three_graph.ThreeGraph.createGlobe, ee.app.assets.javascripts.orbit.utils.three_graph.ThreeGraph.createCityLights, ee.app.assets.javascripts.orbit.utils.three_graph.GraphInteraction

### ee.app.assets.javascripts.orbit.utils.three_graph.CAMERA_ANIM_DURATION_MS
- **Calls**: ee.app.assets.javascripts.orbit.utils.three_graph.constructor, ee.app.assets.javascripts.orbit.utils.three_graph.GraphScene, ee.app.assets.javascripts.orbit.utils.three_graph.ThreeGraph.init, ee.app.assets.javascripts.orbit.utils.three_graph.Group, ee.app.assets.javascripts.orbit.utils.three_graph.add, ee.app.assets.javascripts.orbit.utils.three_graph.ThreeGraph.createGlobe, ee.app.assets.javascripts.orbit.utils.three_graph.ThreeGraph.createCityLights, ee.app.assets.javascripts.orbit.utils.three_graph.GraphInteraction

### ee.app.assets.javascripts.orbit.utils.three_graph.CAMERA_2D_ZOOM_FACTOR
- **Calls**: ee.app.assets.javascripts.orbit.utils.three_graph.constructor, ee.app.assets.javascripts.orbit.utils.three_graph.GraphScene, ee.app.assets.javascripts.orbit.utils.three_graph.ThreeGraph.init, ee.app.assets.javascripts.orbit.utils.three_graph.Group, ee.app.assets.javascripts.orbit.utils.three_graph.add, ee.app.assets.javascripts.orbit.utils.three_graph.ThreeGraph.createGlobe, ee.app.assets.javascripts.orbit.utils.three_graph.ThreeGraph.createCityLights, ee.app.assets.javascripts.orbit.utils.three_graph.GraphInteraction

### ee.app.assets.javascripts.orbit.utils.three_graph.CAMERA_2D_MIN_FIT_FACTOR
- **Calls**: ee.app.assets.javascripts.orbit.utils.three_graph.constructor, ee.app.assets.javascripts.orbit.utils.three_graph.GraphScene, ee.app.assets.javascripts.orbit.utils.three_graph.ThreeGraph.init, ee.app.assets.javascripts.orbit.utils.three_graph.Group, ee.app.assets.javascripts.orbit.utils.three_graph.add, ee.app.assets.javascripts.orbit.utils.three_graph.ThreeGraph.createGlobe, ee.app.assets.javascripts.orbit.utils.three_graph.ThreeGraph.createCityLights, ee.app.assets.javascripts.orbit.utils.three_graph.GraphInteraction

### ee.app.assets.javascripts.orbit.utils.three_graph.CAMERA_2D_FIT_PADDING
- **Calls**: ee.app.assets.javascripts.orbit.utils.three_graph.constructor, ee.app.assets.javascripts.orbit.utils.three_graph.GraphScene, ee.app.assets.javascripts.orbit.utils.three_graph.ThreeGraph.init, ee.app.assets.javascripts.orbit.utils.three_graph.Group, ee.app.assets.javascripts.orbit.utils.three_graph.add, ee.app.assets.javascripts.orbit.utils.three_graph.ThreeGraph.createGlobe, ee.app.assets.javascripts.orbit.utils.three_graph.ThreeGraph.createCityLights, ee.app.assets.javascripts.orbit.utils.three_graph.GraphInteraction

### ee.app.assets.javascripts.orbit.utils.three_graph.EXPANSION_SPREAD_BASE
- **Calls**: ee.app.assets.javascripts.orbit.utils.three_graph.constructor, ee.app.assets.javascripts.orbit.utils.three_graph.GraphScene, ee.app.assets.javascripts.orbit.utils.three_graph.ThreeGraph.init, ee.app.assets.javascripts.orbit.utils.three_graph.Group, ee.app.assets.javascripts.orbit.utils.three_graph.add, ee.app.assets.javascripts.orbit.utils.three_graph.ThreeGraph.createGlobe, ee.app.assets.javascripts.orbit.utils.three_graph.ThreeGraph.createCityLights, ee.app.assets.javascripts.orbit.utils.three_graph.GraphInteraction

### ee.app.assets.javascripts.orbit.utils.three_graph.EXPANSION_SPREAD_VARIANCE
- **Calls**: ee.app.assets.javascripts.orbit.utils.three_graph.constructor, ee.app.assets.javascripts.orbit.utils.three_graph.GraphScene, ee.app.assets.javascripts.orbit.utils.three_graph.ThreeGraph.init, ee.app.assets.javascripts.orbit.utils.three_graph.Group, ee.app.assets.javascripts.orbit.utils.three_graph.add, ee.app.assets.javascripts.orbit.utils.three_graph.ThreeGraph.createGlobe, ee.app.assets.javascripts.orbit.utils.three_graph.ThreeGraph.createCityLights, ee.app.assets.javascripts.orbit.utils.three_graph.GraphInteraction

### ee.app.assets.javascripts.orbit.utils.three_graph.EXPANSION_FLAT_SPREAD_MULTIPLIER
- **Calls**: ee.app.assets.javascripts.orbit.utils.three_graph.constructor, ee.app.assets.javascripts.orbit.utils.three_graph.GraphScene, ee.app.assets.javascripts.orbit.utils.three_graph.ThreeGraph.init, ee.app.assets.javascripts.orbit.utils.three_graph.Group, ee.app.assets.javascripts.orbit.utils.three_graph.add, ee.app.assets.javascripts.orbit.utils.three_graph.ThreeGraph.createGlobe, ee.app.assets.javascripts.orbit.utils.three_graph.ThreeGraph.createCityLights, ee.app.assets.javascripts.orbit.utils.three_graph.GraphInteraction

### ee.app.assets.javascripts.orbit.utils.three_graph.TANGENT_VECTOR_THRESHOLD
- **Calls**: ee.app.assets.javascripts.orbit.utils.three_graph.constructor, ee.app.assets.javascripts.orbit.utils.three_graph.GraphScene, ee.app.assets.javascripts.orbit.utils.three_graph.ThreeGraph.init, ee.app.assets.javascripts.orbit.utils.three_graph.Group, ee.app.assets.javascripts.orbit.utils.three_graph.add, ee.app.assets.javascripts.orbit.utils.three_graph.ThreeGraph.createGlobe, ee.app.assets.javascripts.orbit.utils.three_graph.ThreeGraph.createCityLights, ee.app.assets.javascripts.orbit.utils.three_graph.GraphInteraction

### spec.frontend.diffs.components.diff_file_spec.findDiffHeader
- **Calls**: spec.frontend.diffs.components.diff_file_spec.describe, spec.frontend.diffs.components.diff_file_spec.useLegacyDiffs, spec.frontend.diffs.components.diff_file_spec.changeViewer, spec.frontend.diffs.components.diff_file_spec.useNotes, spec.frontend.diffs.components.diff_file_spec.shallowMountExtended, spec.frontend.diffs.components.diff_file_spec.beforeEach, spec.frontend.diffs.components.diff_file_spec.createTestingPinia, spec.frontend.diffs.components.diff_file_spec.getReadableFile

### spec.frontend.pages.projects.shared.permissions.components.settings_panel_spec.FEATURE_ACCESS_LEVEL_ANONYMOUS
- **Calls**: spec.frontend.pages.projects.shared.permissions.components.settings_panel_spec.describe, spec.frontend.pages.projects.shared.permissions.components.settings_panel_spec.mountFn, spec.frontend.pages.projects.shared.permissions.components.settings_panel_spec.findComponent, spec.frontend.pages.projects.shared.permissions.components.settings_panel_spec.findLFSSettingsRow, spec.frontend.pages.projects.shared.permissions.components.settings_panel_spec.find, spec.frontend.pages.projects.shared.permissions.components.settings_panel_spec.findRepositoryFeatureProjectRow, spec.frontend.pages.projects.shared.permissions.components.settings_panel_spec.findContainerRegistrySettings, spec.frontend.pages.projects.shared.permissions.components.settings_panel_spec.findByTestId

### spec.frontend.vue_merge_request_widget.components.states.mr_widget_ready_to_merge_spec.findCommitEditWithInputId
- **Calls**: spec.frontend.vue_merge_request_widget.components.states.mr_widget_ready_to_merge_spec.describe, spec.frontend.vue_merge_request_widget.components.states.mr_widget_ready_to_merge_spec.beforeEach, spec.frontend.vue_merge_request_widget.components.states.mr_widget_ready_to_merge_spec.createTestService, spec.frontend.vue_merge_request_widget.components.states.mr_widget_ready_to_merge_spec.fn, spec.frontend.vue_merge_request_widget.components.states.mr_widget_ready_to_merge_spec.mockResolvedValueOnce, spec.frontend.vue_merge_request_widget.components.states.mr_widget_ready_to_merge_spec.it, spec.frontend.vue_merge_request_widget.components.states.mr_widget_ready_to_merge_spec.createComponent, spec.frontend.vue_merge_request_widget.components.states.mr_widget_ready_to_merge_spec.expect

### spec.frontend.vue_merge_request_widget.components.states.mr_widget_ready_to_merge_spec.findMergeCommitMessage
- **Calls**: spec.frontend.vue_merge_request_widget.components.states.mr_widget_ready_to_merge_spec.describe, spec.frontend.vue_merge_request_widget.components.states.mr_widget_ready_to_merge_spec.beforeEach, spec.frontend.vue_merge_request_widget.components.states.mr_widget_ready_to_merge_spec.createTestService, spec.frontend.vue_merge_request_widget.components.states.mr_widget_ready_to_merge_spec.fn, spec.frontend.vue_merge_request_widget.components.states.mr_widget_ready_to_merge_spec.mockResolvedValueOnce, spec.frontend.vue_merge_request_widget.components.states.mr_widget_ready_to_merge_spec.it, spec.frontend.vue_merge_request_widget.components.states.mr_widget_ready_to_merge_spec.createComponent, spec.frontend.vue_merge_request_widget.components.states.mr_widget_ready_to_merge_spec.expect

### spec.frontend.vue_merge_request_widget.components.states.mr_widget_ready_to_merge_spec.findSquashCommitMessage
- **Calls**: spec.frontend.vue_merge_request_widget.components.states.mr_widget_ready_to_merge_spec.describe, spec.frontend.vue_merge_request_widget.components.states.mr_widget_ready_to_merge_spec.beforeEach, spec.frontend.vue_merge_request_widget.components.states.mr_widget_ready_to_merge_spec.createTestService, spec.frontend.vue_merge_request_widget.components.states.mr_widget_ready_to_merge_spec.fn, spec.frontend.vue_merge_request_widget.components.states.mr_widget_ready_to_merge_spec.mockResolvedValueOnce, spec.frontend.vue_merge_request_widget.components.states.mr_widget_ready_to_merge_spec.it, spec.frontend.vue_merge_request_widget.components.states.mr_widget_ready_to_merge_spec.createComponent, spec.frontend.vue_merge_request_widget.components.states.mr_widget_ready_to_merge_spec.expect

### spec.frontend.ci.runner.admin_runners.admin_runners_app_spec.STATUS_COUNT_QUERIES
- **Calls**: spec.frontend.ci.runner.admin_runners.admin_runners_app_spec.describe, spec.frontend.ci.runner.admin_runners.admin_runners_app_spec.fn, spec.frontend.ci.runner.admin_runners.admin_runners_app_spec.findComponent, spec.frontend.ci.runner.admin_runners.admin_runners_app_spec.extendedWrapper, spec.frontend.ci.runner.admin_runners.admin_runners_app_spec.findRunnerPagination, spec.frontend.ci.runner.admin_runners.admin_runners_app_spec.findByText, spec.frontend.ci.runner.admin_runners.admin_runners_app_spec.createLocalState, spec.frontend.ci.runner.admin_runners.admin_runners_app_spec.mountFn

### spec.frontend.ci.runner.admin_runners.admin_runners_app_spec.TAB_COUNT_QUERIES
- **Calls**: spec.frontend.ci.runner.admin_runners.admin_runners_app_spec.describe, spec.frontend.ci.runner.admin_runners.admin_runners_app_spec.fn, spec.frontend.ci.runner.admin_runners.admin_runners_app_spec.findComponent, spec.frontend.ci.runner.admin_runners.admin_runners_app_spec.extendedWrapper, spec.frontend.ci.runner.admin_runners.admin_runners_app_spec.findRunnerPagination, spec.frontend.ci.runner.admin_runners.admin_runners_app_spec.findByText, spec.frontend.ci.runner.admin_runners.admin_runners_app_spec.createLocalState, spec.frontend.ci.runner.admin_runners.admin_runners_app_spec.mountFn

### spec.frontend.ci.runner.admin_runners.admin_runners_app_spec.COUNT_QUERIES
- **Calls**: spec.frontend.ci.runner.admin_runners.admin_runners_app_spec.describe, spec.frontend.ci.runner.admin_runners.admin_runners_app_spec.fn, spec.frontend.ci.runner.admin_runners.admin_runners_app_spec.findComponent, spec.frontend.ci.runner.admin_runners.admin_runners_app_spec.extendedWrapper, spec.frontend.ci.runner.admin_runners.admin_runners_app_spec.findRunnerPagination, spec.frontend.ci.runner.admin_runners.admin_runners_app_spec.findByText, spec.frontend.ci.runner.admin_runners.admin_runners_app_spec.createLocalState, spec.frontend.ci.runner.admin_runners.admin_runners_app_spec.mountFn

### ee.app.assets.javascripts.orbit.utils.three_interaction.ARROW_OFFSET
- **Calls**: ee.app.assets.javascripts.orbit.utils.three_interaction.constructor, ee.app.assets.javascripts.orbit.utils.three_interaction.Plane, ee.app.assets.javascripts.orbit.utils.three_interaction.Raycaster, ee.app.assets.javascripts.orbit.utils.three_interaction.Vector3, ee.app.assets.javascripts.orbit.utils.three_interaction.now, ee.app.assets.javascripts.orbit.utils.three_interaction.bind, ee.app.assets.javascripts.orbit.utils.three_interaction.setContext, ee.app.assets.javascripts.orbit.utils.three_interaction.GraphInteraction.onNodeHover

### app.assets.javascripts.diff.UNFOLD_COUNT
- **Calls**: app.assets.javascripts.diff.constructor, app.assets.javascripts.diff.each, app.assets.javascripts.diff.data, app.assets.javascripts.diff.SingleFileDiff, app.assets.javascripts.diff.getElementById, app.assets.javascripts.diff.init, app.assets.javascripts.diff.first, app.assets.javascripts.diff.get

### app.assets.javascripts.diff.isBound
- **Calls**: app.assets.javascripts.diff.constructor, app.assets.javascripts.diff.each, app.assets.javascripts.diff.data, app.assets.javascripts.diff.SingleFileDiff, app.assets.javascripts.diff.getElementById, app.assets.javascripts.diff.init, app.assets.javascripts.diff.first, app.assets.javascripts.diff.get

### spec.frontend.awards_handler_spec.awardsHandler
- **Calls**: spec.frontend.awards_handler_spec.describe, spec.frontend.awards_handler_spec.useFakeRequestAnimationFrame, spec.frontend.awards_handler_spec.eq, spec.frontend.awards_handler_spec.click, spec.frontend.awards_handler_spec.runOnlyPendingTimers, spec.frontend.awards_handler_spec.Promise, spec.frontend.awards_handler_spec.one, spec.frontend.awards_handler_spec.resolve

### spec.frontend.alerts_settings.components.alerts_settings_form_spec.scrollIntoViewMock
- **Calls**: spec.frontend.alerts_settings.components.alerts_settings_form_spec.describe, spec.frontend.alerts_settings.components.alerts_settings_form_spec.fn, spec.frontend.alerts_settings.components.alerts_settings_form_spec.mockResolvedValue, spec.frontend.alerts_settings.components.alerts_settings_form_spec.currentIntegration, spec.frontend.alerts_settings.components.alerts_settings_form_spec.createMockApollo, spec.frontend.alerts_settings.components.alerts_settings_form_spec.mountExtended, spec.frontend.alerts_settings.components.alerts_settings_form_spec.waitForPromises, spec.frontend.alerts_settings.components.alerts_settings_form_spec.findComponent

## Process Flows

Key execution flows identified:

### Flow 1: process
```
process [public.-.speedscope.speedscope.026f36b0]
```

### Flow 2: DEFAULT_PER_PAGE
```
DEFAULT_PER_PAGE [app.assets.javascripts.api]
```

### Flow 3: jobArtifactsCountLimit
```
jobArtifactsCountLimit [spec.frontend.ci.artifacts.components.job_artifacts_table_spec]
```

### Flow 4: t
```
t [public.-.speedscope.import.e3a73ef4]
```

### Flow 5: UsersSelect
```
UsersSelect [app.assets.javascripts.users_select]
```

### Flow 6: CONNECTIONS_RENDER_ORDER
```
CONNECTIONS_RENDER_ORDER [ee.app.assets.javascripts.orbit.utils.three_graph]
  └─ →> init
      └─> createGlobe
      └─> createCityLights
```

### Flow 7: IMPULSES_RENDER_ORDER
```
IMPULSES_RENDER_ORDER [ee.app.assets.javascripts.orbit.utils.three_graph]
  └─ →> init
      └─> createGlobe
      └─> createCityLights
```

### Flow 8: EDGE_LABELS_RENDER_ORDER
```
EDGE_LABELS_RENDER_ORDER [ee.app.assets.javascripts.orbit.utils.three_graph]
  └─ →> init
      └─> createGlobe
      └─> createCityLights
```

### Flow 9: NODE_LABELS_RENDER_ORDER
```
NODE_LABELS_RENDER_ORDER [ee.app.assets.javascripts.orbit.utils.three_graph]
  └─ →> init
      └─> createGlobe
      └─> createCityLights
```

### Flow 10: CAMERA_ANIM_DURATION_MS
```
CAMERA_ANIM_DURATION_MS [ee.app.assets.javascripts.orbit.utils.three_graph]
  └─ →> init
      └─> createGlobe
      └─> createCityLights
```

## Key Classes

### app.models.project.Project
- **Methods**: 441
- **Key Methods**: app.models.project.Project.integration_association_name, app.models.project.Project.with_developer_access, app.models.project.Project.with_api_entity_associations, app.models.project.Project.with_web_entity_associations, app.models.project.Project.with_api_commit_entity_associations, app.models.project.Project.with_api_blob_entity_associations, app.models.project.Project.with_slack_application_disabled, app.models.project.Project.eager_load_namespace_and_owner, app.models.project.Project.public_or_visible_to_user, app.models.project.Project.public_non_forked_or_visible_to_user
- **Inherits**: ApplicationRecord

### app.models.user.User
- **Methods**: 330
- **Key Methods**: app.models.user.User.update_tracked_fields!, app.models.user.User.dashboard, app.models.user.User.effective_dashboard_for_routing, app.models.user.User.dashboard_enum_mapping, app.models.user.User.should_use_flipped_dashboard_mapping_for_rollout?, app.models.user.User.owner_class_attribute_default, app.models.user.User.blocked?, app.models.user.User.supported_keyset_orderings, app.models.user.User.preferred_language, app.models.user.User.active_for_authentication?
- **Inherits**: ApplicationRecord

### app.models.merge_request.MergeRequest
- **Methods**: 308
- **Key Methods**: app.models.merge_request.MergeRequest.suggested_reviewer_users, app.models.merge_request.MergeRequest.merge_request_diff, app.models.merge_request.MergeRequest.available_state_names, app.models.merge_request.MergeRequest.check_state?, app.models.merge_request.MergeRequest.batch_mark_as_unchecked, app.models.merge_request.MergeRequest.batch_mark_as_checking, app.models.merge_request.MergeRequest.batch_clear_merge_error, app.models.merge_request.MergeRequest.public_merge_status, app.models.merge_request.MergeRequest.total_time_to_merge, app.models.merge_request.MergeRequest.reference_prefix
- **Inherits**: ApplicationRecord

### app.models.ci.pipeline.Pipeline
- **Methods**: 186
- **Key Methods**: app.models.ci.pipeline.Pipeline.newest_first, app.models.ci.pipeline.Pipeline.newest_without_schedules, app.models.ci.pipeline.Pipeline.latest_status, app.models.ci.pipeline.Pipeline.latest_successful_for_ref, app.models.ci.pipeline.Pipeline.latest_successful_for_sha, app.models.ci.pipeline.Pipeline.latest_successful_for_refs, app.models.ci.pipeline.Pipeline.latest_pipelines_for_ref_by_statuses, app.models.ci.pipeline.Pipeline.latest_running_for_ref, app.models.ci.pipeline.Pipeline.latest_failed_for_ref, app.models.ci.pipeline.Pipeline.jobs_count_in_alive_pipelines
- **Inherits**: Ci

### app.assets.javascripts.gfm_auto_complete.GfmAutoComplete
- **Methods**: 184
- **Key Methods**: app.assets.javascripts.gfm_auto_complete.GfmAutoComplete.setup, app.assets.javascripts.gfm_auto_complete.GfmAutoComplete.setupLifecycle, app.assets.javascripts.gfm_auto_complete.GfmAutoComplete.setupAtWho, app.assets.javascripts.gfm_auto_complete.GfmAutoComplete.displayTpl, app.assets.javascripts.gfm_auto_complete.GfmAutoComplete.insertTpl, app.assets.javascripts.gfm_auto_complete.GfmAutoComplete.referencePrefix, app.assets.javascripts.gfm_auto_complete.GfmAutoComplete.recordFrequentCommandUsage, app.assets.javascripts.gfm_auto_complete.GfmAutoComplete.match, app.assets.javascripts.gfm_auto_complete.GfmAutoComplete.sorter, app.assets.javascripts.gfm_auto_complete.GfmAutoComplete.prioritized

### app.models.repository.Repository
- **Methods**: 172
- **Key Methods**: app.models.repository.Repository.initialize, app.models.repository.Repository.hash, app.models.repository.Repository.raw_repository, app.models.repository.Repository.flipper_id, app.models.repository.Repository.path_to_repo, app.models.repository.Repository.inspect, app.models.repository.Repository.commit, app.models.repository.Repository.commit_by, app.models.repository.Repository.commits_by, app.models.repository.Repository.commits

### app.models.group.Group
- **Methods**: 153
- **Key Methods**: app.models.group.Group.sti_name, app.models.group.Group.supported_keyset_orderings, app.models.group.Group.with_developer_maintainer_owner_access, app.models.group.Group.sort_by_attribute, app.models.group.Group.public_or_visible_to_user, app.models.group.Group.select_for_project_authorization, app.models.group.Group.without_integration, app.models.group.Group.groups_user_can, app.models.group.Group.preset_root_ancestor_for, app.models.group.Group.ids_with_disabled_email
- **Inherits**: Namespace

### app.assets.javascripts.deprecated_notes.Notes
- **Methods**: 148
- **Key Methods**: app.assets.javascripts.deprecated_notes.Notes.initialize, app.assets.javascripts.deprecated_notes.Notes.getInstance, app.assets.javascripts.deprecated_notes.Notes.hash, app.assets.javascripts.deprecated_notes.Notes.notesList, app.assets.javascripts.deprecated_notes.Notes.renderGFM, app.assets.javascripts.deprecated_notes.Notes.setViewType, app.assets.javascripts.deprecated_notes.Notes.addBinding, app.assets.javascripts.deprecated_notes.Notes.cleanBinding, app.assets.javascripts.deprecated_notes.Notes.initCommentTypeToggle, app.assets.javascripts.deprecated_notes.Notes.el

### app.assets.javascripts.filtered_search.filtered_search_manager.FilteredSearchManager
- **Methods**: 119
- **Key Methods**: app.assets.javascripts.filtered_search.filtered_search_manager.FilteredSearchManager.fullPath, app.assets.javascripts.filtered_search.filtered_search_manager.FilteredSearchManager.setup, app.assets.javascripts.filtered_search.filtered_search_manager.FilteredSearchManager.resultantSearches, app.assets.javascripts.filtered_search.filtered_search_manager.FilteredSearchManager.cleanup, app.assets.javascripts.filtered_search.filtered_search_manager.FilteredSearchManager.bindStateEvents, app.assets.javascripts.filtered_search.filtered_search_manager.FilteredSearchManager.unbindStateEvents, app.assets.javascripts.filtered_search.filtered_search_manager.FilteredSearchManager.applyToStateFilters, app.assets.javascripts.filtered_search.filtered_search_manager.FilteredSearchManager.callback, app.assets.javascripts.filtered_search.filtered_search_manager.FilteredSearchManager.bindEvents, app.assets.javascripts.filtered_search.filtered_search_manager.FilteredSearchManager.unbindEvents

### app.models.namespace.Namespace
- **Methods**: 115
- **Key Methods**: app.models.namespace.Namespace.sti_class_for, app.models.namespace.Namespace.by_path, app.models.namespace.Namespace.find_by_path_or_name, app.models.namespace.Namespace.find_top_level, app.models.namespace.Namespace.root_ids_for, app.models.namespace.Namespace.search, app.models.namespace.Namespace.gfm_autocomplete_search, app.models.namespace.Namespace.clean_path, app.models.namespace.Namespace.reference_prefix, app.models.namespace.Namespace.reference_pattern
- **Inherits**: ApplicationRecord

### app.mailers.previews.notify_preview.NotifyPreview
- **Methods**: 115
- **Key Methods**: app.mailers.previews.notify_preview.NotifyPreview.note_merge_request_email_for_individual_note, app.mailers.previews.notify_preview.NotifyPreview.note_wiki_page_email_for_individual_note, app.mailers.previews.notify_preview.NotifyPreview.new_user_email, app.mailers.previews.notify_preview.NotifyPreview.note_merge_request_email_for_discussion, app.mailers.previews.notify_preview.NotifyPreview.note_merge_request_email_for_diff_discussion, app.mailers.previews.notify_preview.NotifyPreview.resource_access_token_about_to_expire_email, app.mailers.previews.notify_preview.NotifyPreview.access_token_created_email, app.mailers.previews.notify_preview.NotifyPreview.access_token_expired_email, app.mailers.previews.notify_preview.NotifyPreview.access_token_revoked_email, app.mailers.previews.notify_preview.NotifyPreview.access_token_about_to_expire_email
- **Inherits**: ActionMailer

### spec.frontend.behaviors.shortcuts.shortcuts_spec.Subclass
- **Methods**: 108
- **Key Methods**: spec.frontend.behaviors.shortcuts.shortcuts_spec.Subclass.expect, spec.frontend.behaviors.shortcuts.shortcuts_spec.Subclass.describe, spec.frontend.behaviors.shortcuts.shortcuts_spec.Subclass.beforeEach, spec.frontend.behaviors.shortcuts.shortcuts_spec.Subclass.describe, spec.frontend.behaviors.shortcuts.shortcuts_spec.Subclass.beforeEach, spec.frontend.behaviors.shortcuts.shortcuts_spec.Subclass.it, spec.frontend.behaviors.shortcuts.shortcuts_spec.Subclass.expectedCalls, spec.frontend.behaviors.shortcuts.shortcuts_spec.Subclass.expect, spec.frontend.behaviors.shortcuts.shortcuts_spec.Subclass.it, spec.frontend.behaviors.shortcuts.shortcuts_spec.Subclass.flatten

### app.services.notification_service.Async
- **Methods**: 105
- **Key Methods**: app.services.notification_service.Async.initialize, app.services.notification_service.Async.method_missing, app.services.notification_service.Async.async, app.services.notification_service.Async.enabled_two_factor, app.services.notification_service.Async.disabled_two_factor, app.services.notification_service.Async.new_key, app.services.notification_service.Async.new_gpg_key, app.services.notification_service.Async.bot_resource_access_token_about_to_expire, app.services.notification_service.Async.access_token_created, app.services.notification_service.Async.access_token_about_to_expire

### app.models.note.Note
- **Methods**: 102
- **Key Methods**: app.models.note.Note.trigger_note_subscription_create, app.models.note.Note.trigger_note_subscription_update, app.models.note.Note.trigger_note_subscription_destroy, app.models.note.Note.trigger_work_item_updated_subscription, app.models.note.Note.model_name, app.models.note.Note.parent_object_field, app.models.note.Note.grouped_diff_discussions, app.models.note.Note.positions, app.models.note.Note.count_for_collection, app.models.note.Note.search
- **Inherits**: ApplicationRecord

### spec.frontend.editor.source_editor_instance_spec.DummyExt
- **Methods**: 101
- **Key Methods**: spec.frontend.editor.source_editor_instance_spec.DummyExt.extensionName, spec.frontend.editor.source_editor_instance_spec.DummyExt.provides, spec.frontend.editor.source_editor_instance_spec.DummyExt.afterEach, spec.frontend.editor.source_editor_instance_spec.DummyExt.it, spec.frontend.editor.source_editor_instance_spec.DummyExt.expect, spec.frontend.editor.source_editor_instance_spec.DummyExt.expect, spec.frontend.editor.source_editor_instance_spec.DummyExt.expect, spec.frontend.editor.source_editor_instance_spec.DummyExt.describe, spec.frontend.editor.source_editor_instance_spec.DummyExt.it, spec.frontend.editor.source_editor_instance_spec.DummyExt.expect

### ee.app.models.license.License
- **Methods**: 96
- **Key Methods**: ee.app.models.license.License.current, ee.app.models.license.License.current?, ee.app.models.license.License.reset_current, ee.app.models.license.License.cache, ee.app.models.license.License.all_plans, ee.app.models.license.License.block_changes?, ee.app.models.license.License.feature_available?, ee.app.models.license.License.load_license, ee.app.models.license.License.future_dated, ee.app.models.license.License.reset_future_dated
- **Inherits**: ApplicationRecord

### app.models.issue.Issue
- **Methods**: 95
- **Key Methods**: app.models.issue.Issue.most_recent, app.models.issue.Issue.in_namespaces_with_cte, app.models.issue.Issue.with_accessible_sub_namespace_ids_cte, app.models.issue.Issue.order_upvotes_desc, app.models.issue.Issue.order_upvotes_asc, app.models.issue.Issue.full_search, app.models.issue.Issue.related_link_class, app.models.issue.Issue.participant_includes, app.models.issue.Issue.next_object_by_relative_position, app.models.issue.Issue.relative_positioning_parent_projects
- **Inherits**: ApplicationRecord

### app.models.commit.Commit
- **Methods**: 87
- **Key Methods**: app.models.commit.Commit.decorate, app.models.commit.Commit.diff_line_count, app.models.commit.Commit.order_by, app.models.commit.Commit.truncate_sha, app.models.commit.Commit.diff_max_files, app.models.commit.Commit.diff_max_lines, app.models.commit.Commit.max_diff_options, app.models.commit.Commit.diff_safe_max_files, app.models.commit.Commit.diff_safe_max_lines, app.models.commit.Commit.from_hash

### app.models.merge_request_diff.MergeRequestDiff
- **Methods**: 85
- **Key Methods**: app.models.merge_request_diff.MergeRequestDiff.with_users, app.models.merge_request_diff.MergeRequestDiff.ids_for_external_storage_migration, app.models.merge_request_diff.MergeRequestDiff.ids_for_external_storage_migration_strategy_always, app.models.merge_request_diff.MergeRequestDiff.ids_for_external_storage_migration_strategy_outdated, app.models.merge_request_diff.MergeRequestDiff.find_by_diff_refs, app.models.merge_request_diff.MergeRequestDiff.viewable?, app.models.merge_request_diff.MergeRequestDiff.preload_gitaly_data, app.models.merge_request_diff.MergeRequestDiff.save_git_content, app.models.merge_request_diff.MergeRequestDiff.set_patch_id_sha, app.models.merge_request_diff.MergeRequestDiff.get_patch_id_sha
- **Inherits**: ApplicationRecord

### app.assets.javascripts.releases.stores.modules.edit_new.actions.GraphQLError
- **Methods**: 85
- **Key Methods**: app.assets.javascripts.releases.stores.modules.edit_new.actions.GraphQLError.action, app.assets.javascripts.releases.stores.modules.edit_new.actions.GraphQLError.initializeRelease, app.assets.javascripts.releases.stores.modules.edit_new.actions.GraphQLError.dispatch, app.assets.javascripts.releases.stores.modules.edit_new.actions.GraphQLError.fetchRelease, app.assets.javascripts.releases.stores.modules.edit_new.actions.GraphQLError.commit, app.assets.javascripts.releases.stores.modules.edit_new.actions.GraphQLError.fetchResponse, app.assets.javascripts.releases.stores.modules.edit_new.actions.GraphQLError.commit, app.assets.javascripts.releases.stores.modules.edit_new.actions.GraphQLError.commit, app.assets.javascripts.releases.stores.modules.edit_new.actions.GraphQLError.updateReleaseTagName, app.assets.javascripts.releases.stores.modules.edit_new.actions.GraphQLError.commit

## Data Transformation Functions

Key functions that process and transform data:

### jest.config.base.VUE_JEST_TRANSFORMER

### workhorse.internal.zipartifacts.metadata.writeEncoded
- **Output to**: workhorse.internal.zipartifacts.metadata.func, workhorse.internal.zipartifacts.metadata.Marshal, workhorse.internal.zipartifacts.metadata.append, workhorse.internal.zipartifacts.metadata.byte, workhorse.internal.zipartifacts.metadata.writeBytes

### workhorse.internal.zipartifacts.entry.DecodeFileEntry
- **Output to**: workhorse.internal.zipartifacts.entry.DecodeString, workhorse.internal.zipartifacts.entry.string

### workhorse.internal.upstream.roundtripper.roundtripper.mustParseAddress
- **Output to**: workhorse.internal.upstream.roundtripper.roundtripper.SplitHostPort, workhorse.internal.upstream.roundtripper.roundtripper.panic, workhorse.internal.upstream.roundtripper.roundtripper.Errorf

### workhorse.internal.upload.saved_file_tracker.ProcessFile
- **Output to**: workhorse.internal.upload.saved_file_tracker.func, workhorse.internal.upload.saved_file_tracker.Errorf, workhorse.internal.upload.saved_file_tracker.Track

### workhorse.internal.upload.saved_file_tracker.ProcessField
- **Output to**: workhorse.internal.upload.saved_file_tracker.func

### workhorse.internal.upload.saved_file_tracker.TransformContents
- **Output to**: workhorse.internal.upload.saved_file_tracker.func, workhorse.internal.upload.saved_file_tracker.FileTypeFromSuffix, workhorse.internal.upload.saved_file_tracker.handleExifUpload, workhorse.internal.upload.saved_file_tracker.NopCloser

### workhorse.internal.upload.saved_file_tracker.IsLsifProcessing
- **Output to**: workhorse.internal.upload.saved_file_tracker.func

### workhorse.internal.upload.rewrite.parseAndNormalizeContentDisposition
- **Output to**: workhorse.internal.upload.rewrite.ParseMediaType, workhorse.internal.upload.rewrite.Get, workhorse.internal.upload.rewrite.Set, workhorse.internal.upload.rewrite.FormatMediaType

### workhorse.internal.upload.body_uploader.processRequestBody
- **Output to**: workhorse.internal.upload.body_uploader.Prepare, workhorse.internal.upload.body_uploader.Request, workhorse.internal.upload.body_uploader.Errorf, workhorse.internal.upload.body_uploader.Upload, workhorse.internal.upload.body_uploader.Context

### workhorse.internal.upload.artifacts_uploader.ProcessFile
- **Output to**: workhorse.internal.upload.artifacts_uploader.func, workhorse.internal.upload.artifacts_uploader.Errorf, workhorse.internal.upload.artifacts_uploader.Count, workhorse.internal.upload.artifacts_uploader.Track, workhorse.internal.upload.artifacts_uploader.Done

### workhorse.internal.upload.artifacts_uploader.TransformContents
- **Output to**: workhorse.internal.upload.artifacts_uploader.func, workhorse.internal.upload.artifacts_uploader.NewParser

### workhorse.internal.upload.artifacts_uploader.IsLsifProcessing
- **Output to**: workhorse.internal.upload.artifacts_uploader.func

### workhorse.internal.upload.exif.exif.startProcessing
- **Output to**: workhorse.internal.upload.exif.exif.func, workhorse.internal.upload.exif.exif.CommandContext, workhorse.internal.upload.exif.exif.append, workhorse.internal.upload.exif.exif.StdoutPipe, workhorse.internal.upload.exif.exif.Errorf

### workhorse.internal.upload.destination.destination.getClientInformation
- **Output to**: workhorse.internal.upload.destination.destination.IsLocalTempFile, workhorse.internal.upload.destination.destination.newLocalFile, workhorse.internal.upload.destination.destination.UseWorkhorseClientEnabled, workhorse.internal.upload.destination.destination.IsGoCloud, workhorse.internal.upload.destination.destination.Sprintf

### workhorse.internal.transformers.logging.NewTransformLogger

### workhorse.internal.transformers.base_parser.NewBaseParser
- **Output to**: workhorse.internal.transformers.base_parser.createAndUnlinkTempFile, workhorse.internal.transformers.base_parser.func, workhorse.internal.transformers.base_parser.Close, workhorse.internal.transformers.base_parser.Copy, workhorse.internal.transformers.base_parser.NewTransformLogger

### workhorse.internal.transformers.base_parser.transform
- **Output to**: workhorse.internal.transformers.base_parser.func, workhorse.internal.transformers.base_parser.NewWriter, workhorse.internal.transformers.base_parser.Serialize, workhorse.internal.transformers.base_parser.Close, workhorse.internal.transformers.base_parser.CloseWithError

### workhorse.internal.staticpages.servefile.validatePath
- **Output to**: workhorse.internal.staticpages.servefile.func, workhorse.internal.staticpages.servefile.Clean, workhorse.internal.staticpages.servefile.HasPrefix, workhorse.internal.staticpages.servefile.Errorf

### workhorse.internal.transport.transport.validateIPAddress
- **Output to**: workhorse.internal.transport.transport.func, workhorse.internal.transport.transport.SplitHostPort, workhorse.internal.transport.transport.ParseIP, workhorse.internal.transport.transport.Contains, workhorse.internal.transport.transport.URLMustParse

### workhorse.internal.transport.transport.parseCIDR
- **Output to**: workhorse.internal.transport.transport.ParseCIDR, workhorse.internal.transport.transport.panic, workhorse.internal.transport.transport.Sprintf

### workhorse.internal.ratelimitcache.roundtripper.parseRetryAfter
- **Output to**: workhorse.internal.ratelimitcache.roundtripper.ParseInt, workhorse.internal.ratelimitcache.roundtripper.WithError, workhorse.internal.ratelimitcache.roundtripper.Info, workhorse.internal.ratelimitcache.roundtripper.Now, workhorse.internal.ratelimitcache.roundtripper.Add

### workhorse.internal.redis.keywatcher.Process
- **Output to**: workhorse.internal.redis.keywatcher.func, workhorse.internal.redis.keywatcher.Info, workhorse.internal.redis.keywatcher.Background, workhorse.internal.redis.keywatcher.getNumSubscribers, workhorse.internal.redis.keywatcher.processSubscriptions

### workhorse.internal.redis.keywatcher.processSubscriptions
- **Output to**: workhorse.internal.redis.keywatcher.func, workhorse.internal.redis.keywatcher.Info, workhorse.internal.redis.keywatcher.Subscribe, workhorse.internal.redis.keywatcher.Ping, workhorse.internal.redis.keywatcher.WithError

### workhorse.internal.redis.redis.ProcessHook
- **Output to**: workhorse.internal.redis.redis.func, workhorse.internal.redis.redis.Now, workhorse.internal.redis.redis.Inc, workhorse.internal.redis.redis.next, workhorse.internal.redis.redis.isApdexExcluded

## Behavioral Patterns

### state_machine_Tab
- **Type**: state_machine
- **Confidence**: 0.70
- **Functions**: vendor.assets.javascripts.bootstrap.js.src.tab.Tab.VERSION, vendor.assets.javascripts.bootstrap.js.src.tab.Tab.show, vendor.assets.javascripts.bootstrap.js.src.tab.Tab.selector, vendor.assets.javascripts.bootstrap.js.src.tab.Tab.itemSelector, vendor.assets.javascripts.bootstrap.js.src.tab.Tab.complete

### state_machine_Collapse
- **Type**: state_machine
- **Confidence**: 0.70
- **Functions**: vendor.assets.javascripts.bootstrap.js.src.collapse.Collapse.elem, vendor.assets.javascripts.bootstrap.js.src.collapse.Collapse.selector, vendor.assets.javascripts.bootstrap.js.src.collapse.Collapse.VERSION, vendor.assets.javascripts.bootstrap.js.src.collapse.Collapse.Default, vendor.assets.javascripts.bootstrap.js.src.collapse.Collapse.toggle

### state_machine_Modal
- **Type**: state_machine
- **Confidence**: 0.70
- **Functions**: vendor.assets.javascripts.bootstrap.js.src.modal.Modal.VERSION, vendor.assets.javascripts.bootstrap.js.src.modal.Modal.Default, vendor.assets.javascripts.bootstrap.js.src.modal.Modal.toggle, vendor.assets.javascripts.bootstrap.js.src.modal.Modal.show, vendor.assets.javascripts.bootstrap.js.src.modal.Modal.hide

### state_machine_UserPresenter
- **Type**: state_machine
- **Confidence**: 0.70
- **Functions**: spec.rubocop.cop.gitlab.no_helpers_in_presenters_spec.UserPresenter.initialize, spec.rubocop.cop.gitlab.no_helpers_in_presenters_spec.UserPresenter.formatted_name

### state_machine_InjectEnterpriseEditionModule
- **Type**: state_machine
- **Confidence**: 0.70
- **Functions**: rubocop.cop.inject_enterprise_edition_module.InjectEnterpriseEditionModule.ee_const?, rubocop.cop.inject_enterprise_edition_module.InjectEnterpriseEditionModule.on_send, rubocop.cop.inject_enterprise_edition_module.InjectEnterpriseEditionModule.verify_line_number, rubocop.cop.inject_enterprise_edition_module.InjectEnterpriseEditionModule.verify_argument_type, rubocop.cop.inject_enterprise_edition_module.InjectEnterpriseEditionModule.check_method?

### state_machine_NoHelpersInPresenters
- **Type**: state_machine
- **Confidence**: 0.70
- **Functions**: rubocop.cop.gitlab.no_helpers_in_presenters.NoHelpersInPresenters.on_send, rubocop.cop.gitlab.no_helpers_in_presenters.NoHelpersInPresenters.check_include_or_extend_statement, rubocop.cop.gitlab.no_helpers_in_presenters.NoHelpersInPresenters.check_require_statement, rubocop.cop.gitlab.no_helpers_in_presenters.NoHelpersInPresenters.helper_module?, rubocop.cop.gitlab.no_helpers_in_presenters.NoHelpersInPresenters.helper_file?

### state_machine_RescueStatementTimeout
- **Type**: state_machine
- **Confidence**: 0.70
- **Functions**: rubocop.cop.database.rescue_statement_timeout.RescueStatementTimeout.on_resbody, rubocop.cop.database.rescue_statement_timeout.RescueStatementTimeout.targets_exception?

### state_machine_Jira
- **Type**: state_machine
- **Confidence**: 0.70
- **Functions**: qa.qa.page.project.settings.services.jira.Jira.setup_service_with, qa.qa.page.project.settings.services.jira.Jira.enable_jira_issues, qa.qa.page.project.settings.services.jira.Jira.set_jira_project_keys, qa.qa.page.project.settings.services.jira.Jira.click_save_changes_and_wait, qa.qa.page.project.settings.services.jira.Jira.set_jira_server_url

### state_machine_VSCode
- **Type**: state_machine
- **Confidence**: 0.70
- **Functions**: qa.qa.page.project.web_ide.vscode.VSCode.has_pending_changes?, qa.qa.page.project.web_ide.vscode.VSCode.open_file_from_explorer, qa.qa.page.project.web_ide.vscode.VSCode.click_inside_editor_frame, qa.qa.page.project.web_ide.vscode.VSCode.within_file_editor, qa.qa.page.project.web_ide.vscode.VSCode.has_right_click_menu_item?

### state_machine_NewOnDemandScan
- **Type**: state_machine
- **Confidence**: 0.70
- **Functions**: qa.qa.ee.page.project.secure.new_on_demand_scan.NewOnDemandScan.enter_scan_name, qa.qa.ee.page.project.secure.new_on_demand_scan.NewOnDemandScan.create_scanner_profile, qa.qa.ee.page.project.secure.new_on_demand_scan.NewOnDemandScan.create_site_profile, qa.qa.ee.page.project.secure.new_on_demand_scan.NewOnDemandScan.save_and_run_scan, qa.qa.ee.page.project.secure.new_on_demand_scan.NewOnDemandScan.save_scan

### state_machine_IndexWorkItemsMilestoneState
- **Type**: state_machine
- **Confidence**: 0.70
- **Functions**: ee.elastic.migrate.20250717120142_index_work_items_milestone_state.IndexWorkItemsMilestoneState.index_name, ee.elastic.migrate.20250717120142_index_work_items_milestone_state.IndexWorkItemsMilestoneState.new_mappings

### state_machine_AddIndexOnLastSyncedAtToTerraformStateVersionRegistry
- **Type**: state_machine
- **Confidence**: 0.70
- **Functions**: ee.db.geo.post_migrate.20250204110014_add_index_on_last_synced_at_to_terraform_state_version_registry.AddIndexOnLastSyncedAtToTerraformStateVersionRegistry.up, ee.db.geo.post_migrate.20250204110014_add_index_on_last_synced_at_to_terraform_state_version_registry.AddIndexOnLastSyncedAtToTerraformStateVersionRegistry.down

### state_machine_AddIndexOnVerifiedAtToTerraformStateVersionRegistry
- **Type**: state_machine
- **Confidence**: 0.70
- **Functions**: ee.db.geo.post_migrate.20250130163310_add_index_on_verified_at_to_terraform_state_version_registry.AddIndexOnVerifiedAtToTerraformStateVersionRegistry.up, ee.db.geo.post_migrate.20250130163310_add_index_on_verified_at_to_terraform_state_version_registry.AddIndexOnVerifiedAtToTerraformStateVersionRegistry.down

### state_machine_AddLfsObjectStateIndex
- **Type**: state_machine
- **Confidence**: 0.70
- **Functions**: ee.db.geo.post_migrate.20210125222907_add_lfs_object_state_index.AddLfsObjectStateIndex.up, ee.db.geo.post_migrate.20210125222907_add_lfs_object_state_index.AddLfsObjectStateIndex.down

### state_machine_AddUniqueIndexOnTerraformStateVersionRegistry
- **Type**: state_machine
- **Confidence**: 0.70
- **Functions**: ee.db.geo.post_migrate.20210217020156_add_unique_index_on_terraform_state_version_registry.AddUniqueIndexOnTerraformStateVersionRegistry.up, ee.db.geo.post_migrate.20210217020156_add_unique_index_on_terraform_state_version_registry.AddUniqueIndexOnTerraformStateVersionRegistry.down

## Public API Surface

Functions exposed as public API (no underscore prefix):

- `public.-.speedscope.speedscope.026f36b0.process` - 152 calls
- `app.assets.javascripts.api.DEFAULT_PER_PAGE` - 118 calls
- `spec.support.helpers.graphql_helpers.wrap_query` - 92 calls
- `spec.frontend.ci.artifacts.components.job_artifacts_table_spec.jobArtifactsCountLimit` - 89 calls
- `public.-.speedscope.import.e3a73ef4.t` - 89 calls
- `app.assets.javascripts.users_select.UsersSelect` - 82 calls
- `ee.app.assets.javascripts.orbit.utils.three_graph.CONNECTIONS_RENDER_ORDER` - 79 calls
- `ee.app.assets.javascripts.orbit.utils.three_graph.IMPULSES_RENDER_ORDER` - 79 calls
- `ee.app.assets.javascripts.orbit.utils.three_graph.EDGE_LABELS_RENDER_ORDER` - 79 calls
- `ee.app.assets.javascripts.orbit.utils.three_graph.NODE_LABELS_RENDER_ORDER` - 79 calls
- `ee.app.assets.javascripts.orbit.utils.three_graph.CAMERA_ANIM_DURATION_MS` - 79 calls
- `ee.app.assets.javascripts.orbit.utils.three_graph.CAMERA_2D_ZOOM_FACTOR` - 79 calls
- `ee.app.assets.javascripts.orbit.utils.three_graph.CAMERA_2D_MIN_FIT_FACTOR` - 79 calls
- `ee.app.assets.javascripts.orbit.utils.three_graph.CAMERA_2D_FIT_PADDING` - 79 calls
- `ee.app.assets.javascripts.orbit.utils.three_graph.EXPANSION_SPREAD_BASE` - 79 calls
- `ee.app.assets.javascripts.orbit.utils.three_graph.EXPANSION_SPREAD_VARIANCE` - 79 calls
- `ee.app.assets.javascripts.orbit.utils.three_graph.EXPANSION_FLAT_SPREAD_MULTIPLIER` - 79 calls
- `ee.app.assets.javascripts.orbit.utils.three_graph.TANGENT_VECTOR_THRESHOLD` - 79 calls
- `spec.frontend.diffs.components.diff_file_spec.findDiffHeader` - 73 calls
- `spec.frontend.diffs.components.diff_file_spec.findDiffContentArea` - 72 calls
- `spec.frontend.diffs.components.diff_file_spec.findLoader` - 72 calls
- `spec.frontend.diffs.components.diff_file_spec.findToggleButton` - 72 calls
- `spec.frontend.diffs.components.diff_file_spec.findNoteForm` - 72 calls
- `spec.frontend.diffs.components.diff_file_spec.toggleFile` - 72 calls
- `spec.frontend.diffs.components.diff_file_spec.getReadableFile` - 72 calls
- `spec.frontend.diffs.components.diff_file_spec.getUnreadableFile` - 72 calls
- `spec.frontend.diffs.components.diff_file_spec.triggerSaveNote` - 72 calls
- `spec.frontend.diffs.components.diff_file_spec.triggerSaveDraftNote` - 72 calls
- `spec.frontend.pages.projects.shared.permissions.components.settings_panel_spec.FEATURE_ACCESS_LEVEL_ANONYMOUS` - 67 calls
- `spec.frontend.vue_merge_request_widget.components.states.mr_widget_ready_to_merge_spec.findCommitEditWithInputId` - 61 calls
- `spec.frontend.vue_merge_request_widget.components.states.mr_widget_ready_to_merge_spec.findMergeCommitMessage` - 61 calls
- `spec.frontend.vue_merge_request_widget.components.states.mr_widget_ready_to_merge_spec.findSquashCommitMessage` - 61 calls
- `spec.frontend.vue_merge_request_widget.components.states.mr_widget_ready_to_merge_spec.findMergeButton` - 60 calls
- `spec.frontend.vue_merge_request_widget.components.states.mr_widget_ready_to_merge_spec.findMergeImmediatelyDropdown` - 60 calls
- `spec.frontend.vue_merge_request_widget.components.states.mr_widget_ready_to_merge_spec.findSourceBranchDeletedText` - 60 calls
- `spec.frontend.vue_merge_request_widget.components.states.mr_widget_ready_to_merge_spec.findPipelineFailedConfirmModal` - 60 calls
- `spec.frontend.vue_merge_request_widget.components.states.mr_widget_ready_to_merge_spec.findCheckboxElement` - 60 calls
- `spec.frontend.vue_merge_request_widget.components.states.mr_widget_ready_to_merge_spec.findCommitEditElements` - 60 calls
- `spec.frontend.vue_merge_request_widget.components.states.mr_widget_ready_to_merge_spec.findCommitDropdownElement` - 60 calls
- `spec.frontend.vue_merge_request_widget.components.states.mr_widget_ready_to_merge_spec.findFirstCommitEditLabel` - 60 calls

## System Interactions

How components interact:

```mermaid
graph TD
    process --> defineProperty
    process --> Error
    process --> indexOf
    process --> push
    process --> splice
    DEFAULT_PER_PAGE --> group
    DEFAULT_PER_PAGE --> buildUrl
    DEFAULT_PER_PAGE --> replace
    DEFAULT_PER_PAGE --> get
    DEFAULT_PER_PAGE --> then
    jobArtifactsCountLim --> describe
    jobArtifactsCountLim --> fn
    jobArtifactsCountLim --> findComponent
    jobArtifactsCountLim --> findAllComponents
    jobArtifactsCountLim --> findTable
    t --> Uint8Array
    t --> foo
    t --> subarray
    t --> o
    t --> RangeError
    UsersSelect --> toString
    UsersSelect --> match
    UsersSelect --> bind
    UsersSelect --> parse
    UsersSelect --> map
    CONNECTIONS_RENDER_O --> constructor
    CONNECTIONS_RENDER_O --> GraphScene
    CONNECTIONS_RENDER_O --> init
    CONNECTIONS_RENDER_O --> Group
    CONNECTIONS_RENDER_O --> add
```

## Reverse Engineering Guidelines

1. **Entry Points**: Start analysis from the entry points listed above
2. **Core Logic**: Focus on classes with many methods
3. **Data Flow**: Follow data transformation functions
4. **Process Flows**: Use the flow diagrams for execution paths
5. **API Surface**: Public API functions reveal the interface

## Context for LLM

Maintain the identified architectural patterns and public API surface when suggesting changes.