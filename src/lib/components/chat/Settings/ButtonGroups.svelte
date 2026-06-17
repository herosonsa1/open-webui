<script lang="ts">
	import { toast } from 'svelte-sonner';
	import { createEventDispatcher, onMount, getContext } from 'svelte';
	import { v4 as uuidv4 } from 'uuid';
	import { config, settings, skills, tools } from '$lib/stores';
	import { getKnowledgeBases } from '$lib/apis/knowledge';
	import { setButtonGroups } from '$lib/apis/configs';
	import { getBackendConfig } from '$lib/apis';

	const dispatch = createEventDispatcher();
	const i18n = getContext('i18n');

	// 버튼 그룹 구조 정의
	interface ButtonGroup {
		id: string;
		name: string;
		knowledgeIds: string[];
		systemPrompt?: string;
		skillIds?: string[];
		toolIds?: string[];
	}

	let buttonGroups: ButtonGroup[] = [];
	let knowledgeList: any[] = [];
	let skillList: any[] = [];
	let toolList: any[] = [];

	// 편집/추가 폼 상태
	let showForm = false;
	let editingId: string | null = null;
	let name = '';
	let systemPrompt = '';
	let selectedKnowledgeIds: string[] = [];
	let selectedSkillIds: string[] = [];
	let selectedToolIds: string[] = [];

	// API 데이터 로드
	const loadData = async () => {
		try {
			// 지식 베이스 가져오기
			const kbRes = await getKnowledgeBases(localStorage.token).catch(() => null);
			if (kbRes && kbRes.items) {
				knowledgeList = kbRes.items;
			}

			// 스킬 가져오기
			skillList = ($skills ?? []).filter((s) => s.is_active);

			// 툴 가져오기
			toolList = $tools ?? [];
		} catch (error) {
			console.error('데이터 로드 실패:', error);
		}
	};

	// 버튼 그룹 추가 폼 열기
	const openAddForm = () => {
		editingId = null;
		name = '';
		systemPrompt = '';
		selectedKnowledgeIds = [];
		selectedSkillIds = [];
		selectedToolIds = [];
		showForm = true;
	};

	// 버튼 그룹 수정 폼 열기
	const openEditForm = (group: ButtonGroup) => {
		editingId = group.id;
		name = group.name;
		systemPrompt = group.systemPrompt ?? '';
		selectedKnowledgeIds = [...(group.knowledgeIds ?? [])];
		selectedSkillIds = [...(group.skillIds ?? [])];
		selectedToolIds = [...(group.toolIds ?? [])];
		showForm = true;
	};

	// 폼 취소
	const cancelForm = () => {
		showForm = false;
		editingId = null;
	};

	// 버튼 그룹 저장
	const saveGroup = async () => {
		if (!name.trim()) {
			toast.error('버튼 그룹 이름을 입력해 주세요.');
			return;
		}

		let updatedGroups = [...buttonGroups];

		if (editingId) {
			// 수정
			updatedGroups = updatedGroups.map((g) =>
				g.id === editingId
					? {
							...g,
							name: name.trim(),
							systemPrompt: systemPrompt.trim(),
							knowledgeIds: selectedKnowledgeIds,
							skillIds: selectedSkillIds,
							toolIds: selectedToolIds
						}
					: g
			);
		} else {
			// 신규 생성
			const newGroup: ButtonGroup = {
				id: uuidv4(),
				name: name.trim(),
				systemPrompt: systemPrompt.trim(),
				knowledgeIds: selectedKnowledgeIds,
				skillIds: selectedSkillIds,
				toolIds: selectedToolIds
			};
			updatedGroups.push(newGroup);
		}

		const res = await setButtonGroups(localStorage.token, updatedGroups).catch((err) => {
			toast.error(err);
			return null;
		});

		if (res) {
			buttonGroups = res;
			config.set(await getBackendConfig());
			toast.success(editingId ? '버튼 그룹이 수정되었습니다.' : '새 버튼 그룹이 추가되었습니다.');
		}

		showForm = false;
		editingId = null;
	};

	// 버튼 그룹 삭제
	const deleteGroup = async (id: string) => {
		if (confirm('이 버튼 그룹을 삭제하시겠습니까?')) {
			const updatedGroups = buttonGroups.filter((g) => g.id !== id);
			const res = await setButtonGroups(localStorage.token, updatedGroups).catch((err) => {
				toast.error(err);
				return null;
			});

			if (res) {
				buttonGroups = res;
				config.set(await getBackendConfig());
				toast.success('버튼 그룹이 삭제되었습니다.');
			}
		}
	};

	// 지식/스킬/툴 다중 선택 토글용 헬퍼
	const toggleItem = (list: string[], item: string) => {
		if (list.includes(item)) {
			return list.filter((i) => i !== item);
		} else {
			return [...list, item];
		}
	};

	onMount(async () => {
		buttonGroups = $config?.button_groups ?? [];
		await loadData();
	});
</script>

<div class="flex flex-col h-full justify-between text-sm" id="tab-button-groups">
	<div class="overflow-y-auto pr-1 max-h-[30rem] md:max-h-full">
		{#if !showForm}
			<div class="flex justify-between items-center mb-4">
				<div class="text-sm font-semibold text-gray-800 dark:text-gray-200">
					RAG 칩 및 버튼 그룹 설정
				</div>
				<button
					class="px-3 py-1.5 text-xs bg-sky-600 hover:bg-sky-700 text-white rounded-full font-medium transition"
					type="button"
					on:click={openAddForm}
				>
					+ 새 그룹 추가
				</button>
			</div>

			<p class="text-xs text-gray-500 dark:text-gray-400 mb-4">
				대화 입력창 위에 칩으로 표시할 버튼 그룹을 만들 수 있습니다. 버튼을 클릭하면 매핑된 지식 베이스(RAG) 검색이 트리거되고, 설정한 시스템 프롬프트 및 스킬/툴이 대화방에 자동 적용됩니다.
			</p>

			{#if buttonGroups.length === 0}
				<div class="flex flex-col items-center justify-center py-12 border border-dashed border-gray-200 dark:border-gray-800 rounded-2xl">
					<span class="text-gray-400 dark:text-gray-600 text-3xl mb-2">📁</span>
					<span class="text-xs text-gray-500 dark:text-gray-400">등록된 버튼 그룹이 없습니다.</span>
				</div>
			{:else}
				<div class="grid grid-cols-1 gap-3.5">
					{#each buttonGroups as group (group.id)}
						<div class="p-4 rounded-2xl bg-gray-50/50 dark:bg-gray-850/30 border border-gray-100 dark:border-gray-800/50 flex justify-between items-start gap-4">
							<div class="flex-1 min-w-0">
								<div class="font-medium text-sm text-gray-900 dark:text-gray-100 mb-1 truncate">
									{group.name}
								</div>
								
								<div class="flex flex-wrap gap-1.5 mt-2">
									{#if group.knowledgeIds?.length > 0}
										<span class="px-2 py-0.5 text-[10px] font-medium bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 rounded-md border border-emerald-500/20">
											지식 {group.knowledgeIds.length}개
										</span>
									{/if}
									{#if group.systemPrompt}
										<span class="px-2 py-0.5 text-[10px] font-medium bg-blue-500/10 text-blue-600 dark:text-blue-400 rounded-md border border-blue-500/20">
											시스템 프롬프트 지정됨
										</span>
									{/if}
									{#if group.skillIds?.length > 0}
										<span class="px-2 py-0.5 text-[10px] font-medium bg-amber-500/10 text-amber-600 dark:text-amber-400 rounded-md border border-amber-500/20">
											스킬 {group.skillIds.length}개
										</span>
									{/if}
									{#if group.toolIds?.length > 0}
										<span class="px-2 py-0.5 text-[10px] font-medium bg-purple-500/10 text-purple-600 dark:text-purple-400 rounded-md border border-purple-500/20">
											툴 {group.toolIds.length}개
										</span>
									{/if}
								</div>
							</div>
							
							<div class="flex items-center gap-1">
								<button
									class="p-1.5 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg text-gray-600 dark:text-gray-400 transition"
									type="button"
									on:click={() => openEditForm(group)}
									title="수정"
								>
									<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4">
										<path d="M5.433 13.917l1.262-3.155A4 4 0 017.58 9.42l6.92-6.918a2.121 2.121 0 013 3l-6.92 6.918c-.383.383-.84.685-1.343.886l-3.154 1.262a.5.5 0 01-.65-.65z" />
										<path d="M3.5 5.75c0-.69.56-1.25 1.25-1.25H10A.75.75 0 0010 3H4.75A2.75 2.75 0 002 5.75v9.5A2.75 2.75 0 004.75 18h9.5A2.75 2.75 0 0017 15.25V10a.75.75 0 00-1.5 0v5.25c0 .69-.56 1.25-1.25 1.25h-9.5c-.69 0-1.25-.56-1.25-1.25v-9.5z" />
									</svg>
								</button>
								<button
									class="p-1.5 hover:bg-red-500/10 text-red-500 rounded-lg transition"
									type="button"
									on:click={() => deleteGroup(group.id)}
									title="삭제"
								>
									<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4">
										<path fill-rule="evenodd" d="M8.75 1A2.75 2.75 0 006 3.75v.443c-.795.077-1.584.176-2.365.298a.75.75 0 10.23 1.482l.149-.022.841 10.518A2.75 2.75 0 007.596 19h4.807a2.75 2.75 0 002.742-2.53l.841-10.52.149.023a.75.75 0 00.23-1.482A41.03 41.03 0 0014 4.193V3.75A2.75 2.75 0 0011.25 1h-2.5zM10 4c.84 0 1.673.025 2.5.075V3.75c0-.69-.56-1.25-1.25-1.25h-2.5c-.69 0-1.25.56-1.25 1.25v.325C8.327 4.025 9.16 4 10 4zM8.58 7.72a.75.75 0 00-1.006.307l-.938 1.875a.75.75 0 101.342.67l.938-1.875a.75.75 0 00-.336-.977zm3.84 1.028a.75.75 0 00-1.342-.67l-.938 1.875a.75.75 0 101.342.67l.938-1.875z" clip-rule="evenodd" />
									</svg>
								</button>
							</div>
						</div>
					{/each}
				</div>
			{/if}
		{:else}
			<!-- 추가 / 수정 폼 -->
			<div class="space-y-4 mb-4">
				<div class="text-sm font-semibold text-gray-800 dark:text-gray-200">
					{editingId ? '버튼 그룹 수정' : '새 버튼 그룹 추가'}
				</div>

				<div class="space-y-1">
					<label class="text-xs font-semibold text-gray-600 dark:text-gray-400" for="group-name">그룹 이름</label>
					<input
						id="group-name"
						type="text"
						bind:value={name}
						placeholder="예: 개발 가이드 RAG"
						class="w-full text-sm px-3.5 py-2 border dark:border-gray-850 rounded-xl bg-transparent dark:text-gray-100 focus:outline-hidden focus:ring-1 focus:ring-sky-500"
					/>
				</div>

				<div class="space-y-1">
					<label class="text-xs font-semibold text-gray-600 dark:text-gray-400" for="system-prompt">시스템 프롬프트 (선택)</label>
					<textarea
						id="system-prompt"
						bind:value={systemPrompt}
						rows="3"
						placeholder="이 그룹이 활성화되었을 때 AI가 따라야 할 역할을 명시해 주세요."
						class="w-full text-sm px-3.5 py-2 border dark:border-gray-850 rounded-xl bg-transparent dark:text-gray-100 focus:outline-hidden focus:ring-1 focus:ring-sky-500 resize-vertical"
					></textarea>
				</div>

				<!-- RAG 지식 매핑 -->
				<div class="space-y-1.5">
					<label class="text-xs font-semibold text-gray-600 dark:text-gray-400">RAG 지식 베이스 매핑 (다중 선택)</label>
					{#if knowledgeList.length === 0}
						<p class="text-xs text-gray-400 py-1">이용 가능한 지식 베이스가 없습니다. 워크스페이스에서 먼저 생성해 주세요.</p>
					{:else}
						<div class="flex flex-col gap-1.5 max-h-36 overflow-y-auto border border-gray-100 dark:border-gray-850 p-2.5 rounded-xl bg-gray-50/20 dark:bg-gray-900/10">
							{#each knowledgeList as kb (kb.id)}
								<label class="flex items-center gap-2 text-xs text-gray-700 dark:text-gray-300 cursor-pointer hover:text-gray-950 dark:hover:text-gray-100">
									<input
										type="checkbox"
										checked={selectedKnowledgeIds.includes(kb.id)}
										on:change={() => selectedKnowledgeIds = toggleItem(selectedKnowledgeIds, kb.id)}
										class="rounded-sm border-gray-300 text-sky-600 focus:ring-sky-500"
									/>
									<span>{kb.name} <span class="text-[10px] text-gray-400">({kb.collection_name})</span></span>
								</label>
							{/each}
						</div>
					{/if}
				</div>

				<!-- 스킬 매핑 -->
				<div class="space-y-1.5">
					<label class="text-xs font-semibold text-gray-600 dark:text-gray-400">연결할 스킬 매핑 (선택)</label>
					{#if skillList.length === 0}
						<p class="text-xs text-gray-400 py-1">활성화된 스킬이 없습니다.</p>
					{:else}
						<div class="flex flex-col gap-1.5 max-h-32 overflow-y-auto border border-gray-100 dark:border-gray-850 p-2.5 rounded-xl bg-gray-50/20 dark:bg-gray-900/10">
							{#each skillList as skill (skill.id)}
								<label class="flex items-center gap-2 text-xs text-gray-700 dark:text-gray-300 cursor-pointer">
									<input
										type="checkbox"
										checked={selectedSkillIds.includes(skill.id)}
										on:change={() => selectedSkillIds = toggleItem(selectedSkillIds, skill.id)}
										class="rounded-sm border-gray-300 text-sky-600 focus:ring-sky-500"
									/>
									<span>{skill.name}</span>
								</label>
							{/each}
						</div>
					{/if}
				</div>

				<!-- 툴 매핑 -->
				<div class="space-y-1.5">
					<label class="text-xs font-semibold text-gray-600 dark:text-gray-400">연결할 툴 매핑 (선택)</label>
					{#if toolList.length === 0}
						<p class="text-xs text-gray-400 py-1">이용 가능한 툴이 없습니다.</p>
					{:else}
						<div class="flex flex-col gap-1.5 max-h-32 overflow-y-auto border border-gray-100 dark:border-gray-850 p-2.5 rounded-xl bg-gray-50/20 dark:bg-gray-900/10">
							{#each toolList as tool (tool.id)}
								<label class="flex items-center gap-2 text-xs text-gray-700 dark:text-gray-300 cursor-pointer">
									<input
										type="checkbox"
										checked={selectedToolIds.includes(tool.id)}
										on:change={() => selectedToolIds = toggleItem(selectedToolIds, tool.id)}
										class="rounded-sm border-gray-300 text-sky-600 focus:ring-sky-500"
									/>
									<span>{tool.name}</span>
								</label>
							{/each}
						</div>
					{/if}
				</div>
			</div>

			<div class="flex justify-end gap-2 pt-3 border-t border-gray-100 dark:border-gray-850">
				<button
					class="px-3.5 py-1.5 text-xs bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700 transition"
					type="button"
					on:click={cancelForm}
				>
					취소
				</button>
				<button
					class="px-3.5 py-1.5 text-xs bg-sky-600 hover:bg-sky-700 text-white rounded-full transition"
					type="button"
					on:click={saveGroup}
				>
					그룹 저장
				</button>
			</div>
		{/if}
	</div>
</div>
