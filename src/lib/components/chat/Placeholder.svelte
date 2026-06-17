<script lang="ts">
	import { toast } from 'svelte-sonner';
	import { marked } from 'marked';
	import DOMPurify from 'dompurify';

	import { onMount, getContext, tick, createEventDispatcher } from 'svelte';
	import { blur, fade } from 'svelte/transition';

	const dispatch = createEventDispatcher();

	import { getChatList } from '$lib/apis/chats';
	import { updateFolderById } from '$lib/apis/folders';

	import {
		config,
		user,
		models as _models,
		temporaryChatEnabled,
		selectedFolder,
		chats,
		currentChatPage
	} from '$lib/stores';
	import { sanitizeResponseContent, extractCurlyBraceWords } from '$lib/utils';
	import { WEBUI_API_BASE_URL, WEBUI_BASE_URL } from '$lib/constants';

	import Suggestions from './Suggestions.svelte';
	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import EyeSlash from '$lib/components/icons/EyeSlash.svelte';
	import MessageInput from './MessageInput.svelte';
	import FolderPlaceholder from './Placeholder/FolderPlaceholder.svelte';
	import FolderTitle from './Placeholder/FolderTitle.svelte';

	const i18n = getContext('i18n');

	export let createMessagePair: Function;
	export let stopResponse: Function;

	export let autoScroll = false;

	export let atSelectedModel: Model | undefined;
	export let selectedModels: [''];

	export let history;

	export let prompt = '';
	export let files = [];
	export let messageInput = null;

	export let selectedToolIds = [];
	export let selectedSkillIds = [];
	export let selectedFilterIds = [];
	export let pendingOAuthTools = [];

	export let showCommands = false;

	export let imageGenerationEnabled = false;
	export let codeInterpreterEnabled = false;
	export let webSearchEnabled = false;

	export let onUpload: Function = (e) => {};
	export let onSelect = (e) => {};
	export let onChange = (e) => {};

	export let toolServers = [];

	export let dragged = false;

	let models = [];
	let selectedModelIdx = 0;

	$: if (selectedModels.length > 0) {
		selectedModelIdx = models.length - 1;
	}

	$: models = selectedModels.map((id) => $_models.find((m) => m.id === id));
</script>

<div class="m-auto w-full max-w-6xl px-2 @2xl:px-20 translate-y-6 py-24 text-center">
	{#if $temporaryChatEnabled}
		<Tooltip
			content={$i18n.t("This chat won't appear in history and your messages will not be saved.")}
			className="w-full flex justify-center mb-0.5"
			placement="top"
		>
			<div class="flex items-center gap-2 text-gray-500 text-base my-2 w-fit">
				<EyeSlash strokeWidth="2.5" className="size-4" />{$i18n.t('Temporary Chat')}
			</div>
		</Tooltip>
	{/if}

	<div
		class="w-full text-3xl text-gray-800 dark:text-gray-100 text-center flex items-center gap-4 font-primary"
	>
		<div class="w-full flex flex-col justify-center items-center">
			{#if $selectedFolder}
				<FolderTitle
					folder={$selectedFolder}
					onUpdate={async (folder) => {
						await chats.set(await getChatList(localStorage.token, $currentChatPage));
						currentChatPage.set(1);
					}}
					onDelete={async () => {
						await chats.set(await getChatList(localStorage.token, $currentChatPage));
						currentChatPage.set(1);

						selectedFolder.set(null);
					}}
				/>
			{:else}
				<!-- 관리자일 때만 상단 모델 아바타 및 모델 선택 드롭다운 노출 -->
				{#if $user?.role === 'admin'}
					<div class="flex flex-row justify-center gap-2.5 @sm:gap-3 w-fit px-5 max-w-xl mb-4">
						<div class="flex shrink-0 justify-center">
							<div class="flex -space-x-4 mb-0.5" in:fade={{ duration: 100 }}>
								{#each models as model, modelIdx}
									<Tooltip
										content={(models[modelIdx]?.info?.meta?.tags ?? []).map((tag) => tag.name.toUpperCase()).join(', ')}
										placement="top"
									>
										<button
											aria-hidden={models.length <= 1}
											aria-label={$i18n.t('Get information on {{name}} in the UI', {
												name: models[modelIdx]?.name
											})}
											on:click={() => {
												selectedModelIdx = modelIdx;
											}}
										>
											<img
												src={`${WEBUI_API_BASE_URL}/models/model/profile/image?id=${model?.id}&lang=${$i18n.language}`}
												class=" size-9 @sm:size-10 rounded-full border-[1px] border-gray-100 dark:border-none"
												aria-hidden="true"
												draggable="false"
												on:error={(e) => {
													e.currentTarget.src = '/favicon.png';
												}}
											/>
										</button>
									</Tooltip>
								{/each}
							</div>
						</div>

						<div
							class=" text-3xl @sm:text-3xl line-clamp-1 flex items-center"
							in:fade={{ duration: 100 }}
						>
							{#if models[selectedModelIdx]?.name}
								<Tooltip
									content={models[selectedModelIdx]?.name}
									placement="top"
									className=" flex items-center "
								>
									<span class="line-clamp-1 font-semibold">
										{models[selectedModelIdx]?.name}
									</span>
								</Tooltip>
							{/if}
						</div>
					</div>
				{/if}

				<!-- 개인화 웰컴 메시지: 이름 + 직책님 | 소속부서명 -->
				{@const name = $user?.name ?? ''}
				{@const position = $user?.position_name ?? ''}
				{@const org = $user?.org_nm ?? ''}
				<div class="text-3xl @sm:text-4xl font-bold text-gray-800 dark:text-gray-100 font-primary my-2" in:fade={{ duration: 100 }}>
					안녕하세요, {name}<span class="text-xl @sm:text-2xl font-medium text-gray-500 dark:text-gray-400">{position ? ' ' + position : ''}님{org ? ' | ' + org : ''}</span>
				</div>

				<!-- 선택된 모델의 상세 정보 카드 (hello 메시지 하단에 표시) -->
				{#if models[selectedModelIdx]?.info?.meta?.description}
					<div in:fade={{ duration: 150 }} class="mt-4 mx-auto max-w-2xl text-left bg-gray-50 dark:bg-gray-850 border border-gray-100 dark:border-gray-800 p-5 rounded-2xl shadow-xs w-full">
						<div class="text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider mb-2 flex items-center gap-1.5">
							<span class="w-1.5 h-1.5 rounded-full bg-sky-500"></span>
							{models[selectedModelIdx]?.name} 모델 설명
						</div>
						<div class="text-sm text-gray-600 dark:text-gray-300 leading-relaxed markdown">
							{@html DOMPurify.sanitize(
								marked.parse(
									sanitizeResponseContent(
										models[selectedModelIdx]?.info?.meta?.description ?? ''
									).replaceAll('\n', '<br>')
								)
							)}
						</div>
					</div>
				{/if}
			{/if}

			<div class="text-base font-normal @md:max-w-3xl w-full py-3 {atSelectedModel ? 'mt-2' : ''}">
				<MessageInput
					bind:this={messageInput}
					{history}
					bind:selectedModels={selectedModels}
					bind:files
					bind:prompt
					bind:autoScroll
					bind:selectedToolIds
					bind:selectedSkillIds
					bind:selectedFilterIds
					bind:imageGenerationEnabled
					bind:codeInterpreterEnabled
					bind:webSearchEnabled
					bind:atSelectedModel
					bind:showCommands
					bind:dragged
					{pendingOAuthTools}
					{toolServers}
					{stopResponse}
					{createMessagePair}
					placeholder={$i18n.t('How can I help you today?')}
					{onChange}
					{onUpload}
					on:submit={(e) => {
						dispatch('submit', e.detail);
					}}
				/>
			</div>
		</div>
	</div>

	{#if $selectedFolder}
		<div
			class="mx-auto px-4 md:max-w-3xl md:px-6 font-primary min-h-62"
			in:fade={{ duration: 200, delay: 200 }}
		>
			<FolderPlaceholder folder={$selectedFolder} />
		</div>
	{:else}
		<div class="mx-auto max-w-2xl font-primary mt-2" in:fade={{ duration: 200, delay: 200 }}>
			<div class="mx-5">
				<Suggestions
					suggestionPrompts={atSelectedModel?.info?.meta?.suggestion_prompts ??
						models[selectedModelIdx]?.info?.meta?.suggestion_prompts ??
						$config?.default_prompt_suggestions ??
						[]}
					inputValue={prompt}
					{onSelect}
				/>
			</div>
		</div>
	{/if}
</div>
