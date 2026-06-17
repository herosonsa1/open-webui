import { WEBUI_API_BASE_URL } from '$lib/constants';
import { getUserPosition } from '$lib/utils';

export const getUserGroups = async (token: string) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/users/groups`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			error = err.detail;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const getUserDefaultPermissions = async (token: string) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/users/default/permissions`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			error = err.detail;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const updateUserDefaultPermissions = async (token: string, permissions: object) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/users/default/permissions`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		},
		body: JSON.stringify({
			...permissions
		})
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			error = err.detail;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const updateUserRole = async (token: string, id: string, role: string) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/users/update/role`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		},
		body: JSON.stringify({
			id: id,
			role: role
		})
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			error = err.detail;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const getUsers = async (
	token: string,
	query?: string,
	orderBy?: string,
	direction?: string,
	page = 1
) => {
	let error = null;
	let res = null;

	const searchParams = new URLSearchParams();

	searchParams.set('page', `${page}`);

	if (query) {
		searchParams.set('query', query);
	}

	if (orderBy) {
		searchParams.set('order_by', orderBy);
	}

	if (direction) {
		searchParams.set('direction', direction);
	}

	res = await fetch(`${WEBUI_API_BASE_URL}/users/?${searchParams.toString()}`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			error = err.detail;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const searchUsers = async (
	token: string,
	query?: string,
	orderBy?: string,
	direction?: string,
	page = 1
) => {
	let error = null;
	let res = null;

	const searchParams = new URLSearchParams();

	searchParams.set('page', `${page}`);

	if (query) {
		searchParams.set('query', query);
	}

	if (orderBy) {
		searchParams.set('order_by', orderBy);
	}

	if (direction) {
		searchParams.set('direction', direction);
	}

	res = await fetch(`${WEBUI_API_BASE_URL}/users/search?${searchParams.toString()}`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			error = err.detail;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const getAllUsers = async (token: string) => {
	let error = null;
	let res = null;

	res = await fetch(`${WEBUI_API_BASE_URL}/users/all`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			error = err.detail;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const getUserSettings = async (token: string) => {
	let error = null;
	const res = await fetch(`${WEBUI_API_BASE_URL}/users/user/settings`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			error = err.detail;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const updateUserSettings = async (token: string, settings: object) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/users/user/settings/update`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		},
		body: JSON.stringify({
			...settings
		})
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			error = err.detail;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const getUserInfoById = async (token: string, userId: string) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/users/${userId}/info`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			error = err.detail;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const updateUserStatus = async (token: string, formData: object) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/users/user/status/update`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		},
		body: JSON.stringify({
			...formData
		})
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			error = err.detail;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const getUserInfo = async (token: string) => {
	let error = null;
	const res = await fetch(`${WEBUI_API_BASE_URL}/users/user/info`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			error = err.detail;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const updateUserInfo = async (token: string, info: object) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/users/user/info/update`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		},
		body: JSON.stringify({
			...info
		})
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			error = err.detail;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const getAndUpdateUserLocation = async (token: string) => {
	const location = await getUserPosition().catch((err) => {
		console.error(err);
		return null;
	});

	if (location) {
		await updateUserInfo(token, { location: location });
		return location;
	} else {
		console.info('Failed to get user location');
		return null;
	}
};

export const getUserActiveStatusById = async (token: string, userId: string) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/users/${userId}/active`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			error = err.detail;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const deleteUserById = async (token: string, userId: string) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/users/${userId}`, {
		method: 'DELETE',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			error = err.detail;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

type UserUpdateForm = {
	role: string;
	profile_image_url: string;
	email: string;
	name: string;
	password: string;
	position_name?: string;
	org_nm?: string;
	org_cd?: string;
	parent_org_nm?: string;
	phone_number?: string;
	ip_address?: string;
	join_date?: string;
	resign_date?: string;
	sync_lock_yn?: string;
};

export const updateUserById = async (token: string, userId: string, user: UserUpdateForm) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/users/${userId}/update`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		},
		body: JSON.stringify({
			profile_image_url: user.profile_image_url,
			role: user.role,
			email: user.email,
			name: user.name,
			password: user.password !== '' ? user.password : undefined,
			position_name: user.position_name,
			org_nm: user.org_nm,
			org_cd: user.org_cd,
			parent_org_nm: user.parent_org_nm,
			phone_number: user.phone_number,
			ip_address: user.ip_address,
			join_date: user.join_date,
			resign_date: user.resign_date,
			sync_lock_yn: user.sync_lock_yn
		})
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			error = err.detail;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const getUserGroupsById = async (token: string, userId: string) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/users/${userId}/groups`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			error = err.detail;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const getUserPreview = async (token: string, userId: string) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/users/${userId}/preview`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			error = err.detail;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const resetUserPasswordById = async (token: string, userId: string) => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/users/${userId}/reset-password`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			error = err.detail;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const syncUsers = async (token: string) => {
	let error = null;
	const res = await fetch(`${WEBUI_API_BASE_URL}/users/sync`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			error = err.detail || err.message || err;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const updateUserSyncLock = async (token: string, userId: string, syncLock: boolean) => {
	let error = null;
	const res = await fetch(`${WEBUI_API_BASE_URL}/users/${userId}/sync-lock`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		},
		body: JSON.stringify({
			syncLock: syncLock
		})
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			error = err.detail || err.message || err;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const getUserSyncHistory = async (token: string) => {
	let error = null;
	const res = await fetch(`${WEBUI_API_BASE_URL}/users/sync/history`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			error = err.detail || err.message || err;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};
