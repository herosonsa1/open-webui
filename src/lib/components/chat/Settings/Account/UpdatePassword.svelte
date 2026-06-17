<script lang="ts">
	import { getContext } from 'svelte';
	import { toast } from 'svelte-sonner';
	import { updateUserPassword } from '$lib/apis/auths';
	import SensitiveInput from '$lib/components/common/SensitiveInput.svelte';

	const i18n = getContext('i18n');

	let show = false;
	let currentPassword = '';
	let newPassword = '';
	let newPasswordConfirm = '';

	const updatePasswordHandler = async () => {
		// 대문자, 소문자, 숫자, 특수문자 1개 이상 포함, 8자 이상 검증
		const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,}$/;
		if (!passwordRegex.test(newPassword)) {
			toast.error(
				'비밀번호는 대문자, 소문자, 숫자, 특수문자를 각각 1개 이상 포함하여 8자 이상이어야 합니다.'
			);
			newPassword = '';
			newPasswordConfirm = '';
			return;
		}

		if (newPassword === newPasswordConfirm) {
			const res = await updateUserPassword(localStorage.token, currentPassword, newPassword).catch(
				(error) => {
					toast.error(`${error}`);
					return null;
				}
			);

			if (res) {
				toast.success($i18n.t('Successfully updated.'));
			}

			currentPassword = '';
			newPassword = '';
			newPasswordConfirm = '';
		} else {
			toast.error(
				$i18n.t("The passwords you entered don't quite match. Please double-check and try again.")
			);
			newPassword = '';
			newPasswordConfirm = '';
		}
	};
</script>

<form
	class="flex flex-col text-sm"
	on:submit|preventDefault={() => {
		updatePasswordHandler();
	}}
>
	<div class="flex justify-between items-center text-sm">
		<div class="  font-medium">{$i18n.t('Change Password')}</div>
		<button
			class=" text-xs font-medium text-gray-500"
			type="button"
			on:click={() => {
				show = !show;
			}}>{show ? $i18n.t('Hide') : $i18n.t('Show')}</button
		>
	</div>

	{#if show}
		<div class=" py-2.5 space-y-1.5">
			<div class="flex flex-col w-full">
				<div class=" mb-1 text-xs text-gray-500">{$i18n.t('Current Password')}</div>

				<div class="flex-1">
					<SensitiveInput
						class="w-full bg-transparent text-sm dark:text-gray-300 outline-hidden placeholder:opacity-30"
						type="password"
						bind:value={currentPassword}
						placeholder={$i18n.t('Enter your current password')}
						autocomplete="current-password"
						required
					/>
				</div>
			</div>

			<div class="flex flex-col w-full">
				<div class=" mb-1 text-xs text-gray-500">{$i18n.t('New Password')}</div>

				<div class="flex-1">
					<SensitiveInput
						class="w-full bg-transparent text-sm dark:text-gray-300 outline-hidden placeholder:opacity-30"
						type="password"
						bind:value={newPassword}
						placeholder={$i18n.t('Enter your new password')}
						autocomplete="new-password"
						required
					/>
				</div>
				<div class="mt-1 text-[11px] text-gray-400 dark:text-gray-500">
					규칙: 대문자, 소문자, 숫자, 특수문자 각 1개 이상 포함, 8자 이상
				</div>
			</div>

			<div class="flex flex-col w-full">
				<div class=" mb-1 text-xs text-gray-500">{$i18n.t('Confirm Password')}</div>

				<div class="flex-1">
					<SensitiveInput
						class="w-full bg-transparent text-sm dark:text-gray-300 outline-hidden placeholder:opacity-30"
						type="password"
						bind:value={newPasswordConfirm}
						placeholder={$i18n.t('Confirm your new password')}
						autocomplete="off"
						required
					/>
				</div>
			</div>
		</div>

		<div class="mt-3 flex justify-end">
			<button
				class="px-3.5 py-1.5 text-sm font-medium bg-black hover:bg-gray-900 text-white dark:bg-white dark:text-black dark:hover:bg-gray-100 transition rounded-full"
			>
				{$i18n.t('Update password')}
			</button>
		</div>
	{/if}
</form>
