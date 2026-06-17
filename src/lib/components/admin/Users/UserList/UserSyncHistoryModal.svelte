<script lang="ts">
	import { getContext, onMount } from 'svelte';
	import { toast } from 'svelte-sonner';
	import dayjs from 'dayjs';
	import localizedFormat from 'dayjs/plugin/localizedFormat';
	dayjs.extend(localizedFormat);

	import { getUserSyncHistory } from '$lib/apis/users';
	import Modal from '$lib/components/common/Modal.svelte';
	import XMark from '$lib/components/icons/XMark.svelte';
	import Spinner from '$lib/components/common/Spinner.svelte';

	const i18n = getContext('i18n');

	export let show = false;

	let loading = false;
	let logs: any[] = [];

	$: if (show) {
		loadHistory();
	}

	const loadHistory = async () => {
		loading = true;
		try {
			const res = await getUserSyncHistory(localStorage.token);
			if (res) {
				logs = res;
			}
		} catch (error) {
			console.error(error);
			toast.error(`동기화 이력을 가져오는데 실패했습니다: ${error}`);
		} finally {
			loading = false;
		}
	};
</script>

<Modal size="lg" bind:show>
	<div class="flex flex-col h-[80vh] max-h-[600px]">
		<div class="flex justify-between dark:text-gray-300 px-5 pt-4 pb-2 border-b border-gray-100 dark:border-gray-850">
			<div class="text-lg font-medium self-center">사용자 동기화 이력</div>
			<button
				class="self-center"
				aria-label={$i18n.t('Close')}
				on:click={() => {
					show = false;
				}}
			>
				<XMark className="size-5" />
			</button>
		</div>

		<div class="flex-1 overflow-y-auto p-5 dark:text-gray-200">
			{#if loading}
				<div class="flex justify-center items-center h-full my-10">
					<Spinner className="size-8" />
				</div>
			{:else if logs.length === 0}
				<div class="flex justify-center items-center h-full text-gray-500 text-sm my-10">
					동기화 작업 이력이 존재하지 않습니다.
				</div>
			{:else}
				<div class="scrollbar-hidden relative whitespace-nowrap overflow-x-auto max-w-full border border-gray-100 dark:border-gray-850 rounded-xl">
					<table class="w-full text-sm text-left text-gray-500 dark:text-gray-400 table-auto">
						<thead class="text-xs text-gray-800 uppercase bg-gray-50 dark:bg-gray-850 dark:text-gray-200">
							<tr>
								<th scope="col" class="px-4 py-3">실행 일시</th>
								<th scope="col" class="px-4 py-3">작업 유형</th>
								<th scope="col" class="px-4 py-3">상태</th>
								<th scope="col" class="px-4 py-3 text-center">추가 건수</th>
								<th scope="col" class="px-4 py-3 text-center">수정 건수</th>
								<th scope="col" class="px-4 py-3">비고 / 에러 메시지</th>
							</tr>
						</thead>
						<tbody>
							{#each logs as log (log.id)}
								<tr class="bg-white dark:bg-gray-900 border-b border-gray-100 dark:border-gray-850 text-xs">
									<td class="px-4 py-3 font-medium text-gray-900 dark:text-white">
										{dayjs(log.created_at * 1000).format('YYYY-MM-DD HH:mm:ss')}
									</td>
									<td class="px-4 py-3">
										<span class="px-2 py-0.5 rounded-full text-[10px] font-semibold {log.sync_type === 'AUTO' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400' : 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400'}">
											{log.sync_type === 'AUTO' ? '자동배치' : '수동실행'}
										</span>
									</td>
									<td class="px-4 py-3">
										<span class="px-2 py-0.5 rounded-full text-[10px] font-semibold {log.status === 'SUCCESS' ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' : log.status === 'EMPTY' ? 'bg-gray-100 text-gray-800 dark:bg-gray-850 dark:text-gray-400' : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'}">
											{log.status === 'SUCCESS' ? '성공' : log.status === 'EMPTY' ? '변경사항 없음' : '실패'}
										</span>
									</td>
									<td class="px-4 py-3 text-center text-green-600 dark:text-green-400 font-bold">
										{log.appended_count}
									</td>
									<td class="px-4 py-3 text-center text-blue-600 dark:text-blue-400 font-bold">
										{log.updated_count}
									</td>
									<td class="px-4 py-3 text-red-500 dark:text-red-400 whitespace-normal break-all max-w-[250px]">
										{log.error_message || '-'}
									</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			{/if}
		</div>

		<div class="flex justify-end p-4 border-t border-gray-100 dark:border-gray-850">
			<button
				class="px-4 py-1.5 text-sm font-medium bg-black hover:bg-gray-900 text-white dark:bg-white dark:text-black dark:hover:bg-gray-100 transition rounded-full"
				on:click={() => {
					show = false;
				}}
			>
				닫기
			</button>
		</div>
	</div>
</Modal>

<style>
	table {
		width: 100%;
		border-collapse: collapse;
	}
</style>
