import re
import os

def normalize_newlines(text):
    return text.replace('\r\n', '\n')

def patch_message_input():
    filepath = 'src/lib/components/chat/MessageInput.svelte'
    print(f"Patching {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = normalize_newlines(content)
    
    # 1. script section patch
    if 'const selectModel =' not in content:
        target1 = 'export let pendingOAuthTools = [];'
        replacement1 = 'export let pendingOAuthTools = [];\n\n\t$: visibleModels = $models.filter((m) => !m?.preset && m.id !== \'arena\' && !m?.arena);\n\n\tconst selectModel = (modelId: string) => {\n\t\tselectedModels = [modelId];\n\t};'
        content = content.replace(target1, replacement1)
    
    # 2. UI section patch
    if '<!-- 모델 선택 토글 버튼 -->' not in content:
        pattern = r'(<button\s+id="generate-message-pair-button"\s+class="hidden"\s+on:click=\{\(\)\s+=>\s+createMessagePair\(prompt\)\}\s*/>)'
        match = re.search(pattern, content)
        if match:
            original_button = match.group(1)
            ui_code = """
						<!-- 모델 선택 토글 버튼 -->
						{#if visibleModels && visibleModels.length > 0}
							<div class="flex items-center gap-1.5 overflow-x-auto scrollbar-hidden px-2 py-1 mb-1 max-w-full">
								{#each visibleModels as model (model.id)}
									{@const isSelected = selectedModels.includes(model.id)}
									<button
										type="button"
										class="text-[11px] px-3 py-1.5 rounded-full transition-all font-medium shrink-0 border flex items-center gap-1.5
											{isSelected
												? 'bg-sky-500 text-white border-sky-500 dark:bg-sky-600 dark:border-sky-600 shadow-sm'
												: 'bg-transparent text-gray-500 dark:text-gray-400 border-gray-100 dark:border-gray-800/80 hover:bg-gray-50 dark:hover:bg-gray-850'}"
										on:click={() => selectModel(model.id)}
									>
										{#if model.meta?.knowledge && model.meta.knowledge.length > 0}
											<span class="w-1.5 h-1.5 rounded-full {isSelected ? 'bg-sky-200 animate-pulse' : 'bg-sky-500 dark:bg-sky-400'}"></span>
										{/if}
										{model.name}
									</button>
								{/each}
							</div>
						{/if}"""
            content = content.replace(original_button, original_button + ui_code)
        else:
            print("Warning: generate-message-pair-button pattern not found!")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("MessageInput patched successfully.")

def patch_chat():
    filepath = 'src/lib/components/chat/Chat.svelte'
    print(f"Patching {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = normalize_newlines(content)
    
    # 1. remove let activeButtonGroupId = null;
    content = content.replace('let activeButtonGroupId = null;', '')
    
    # 2. remove activeButtonGroupId reactive statement
    pattern_reactive = r'\$:\s*if\s*\(activeButtonGroupId\s*!==\s*undefined\)\s*\{\s*if\s*\(params\)\s*\{\s*params\.activeButtonGroupId\s*=\s*activeButtonGroupId;\s*\}\s*\}'
    content = re.sub(pattern_reactive, '', content)
    
    # Also clean up basic initializations
    content = content.replace('activeButtonGroupId = null;', '')
    content = content.replace('activeButtonGroupId = params?.activeButtonGroupId ?? null;', '')
    
    # 3. remove RAG knowledge injection using regex
    pattern_rag = r'//\s*활성화된\s*버튼\s*그룹의\s*RAG\s*지식\s*매핑\s*주입\s*if\s*\(activeButtonGroupId\)[\s\S]*?status:\s*\'processed\'\s*\}\);\s*\}\s*\}\s*\}\s*\}\s*\}'
    content = re.sub(pattern_rag, '', content)
    
    # 4. remove system prompt injection check
    pattern_prompt = r'let\s*systemPromptContent\s*=\s*params\?\.system\s*\|\|\s*\$settings\.system;\s*if\s*\(activeButtonGroupId\)[\s\S]*?\}\s*:\s*undefined\s*\}\]\.filter\(Boolean\);'
    replacement_prompt = """let messages = [
			params?.system || $settings.system
				? { role: 'system', content: `${params?.system ?? $settings?.system ?? ''}` }
				: undefined
		].filter(Boolean);"""
    content = re.sub(pattern_prompt, replacement_prompt, content)
    
    # 5. remove tool injection check
    pattern_tool = r'let\s*mergedToolIds\s*=\s*\[\.\.\.selectedToolIds\];\s*if\s*\(activeButtonGroupId\)[\s\S]*?mergedToolIds\.push\(tid\);\s*\}\s*\}\s*\}\s*\}\s*\}'
    replacement_tool = "let mergedToolIds = [...selectedToolIds];"
    content = re.sub(pattern_tool, replacement_tool, content)
    
    # 6. remove skill injection check
    pattern_skill = r'const\s*skillIds\s*=\s*\[\.\.\.selectedSkillIds\];\s*if\s*\(activeButtonGroupId\)[\s\S]*?skillIds\.push\(sid\);\s*\}\s*\}\s*\}\s*\}'
    replacement_skill = "const skillIds = [...selectedSkillIds];"
    content = re.sub(pattern_skill, replacement_skill, content)
    
    # 7. update MessageInput instantiation in Chat.svelte
    pattern_mi = r'<MessageInput\s+bind:this=\{messageInput\}\s+bind:activeButtonGroupId\s+\{history\}\s+\{taskIds\}\s+\{selectedModels\}'
    replacement_mi = """<MessageInput
									bind:this={messageInput}
									bind:selectedModels={selectedModels}
									{history}
									{taskIds}"""
    content = re.sub(pattern_mi, replacement_mi, content)
    
    # 8. update Placeholder instantiation in Chat.svelte
    pattern_ph = r'<Placeholder\s+\{history\}\s+\{selectedModels\}\s+bind:messageInput\s+bind:activeButtonGroupId'
    replacement_ph = """<Placeholder
									{history}
									bind:selectedModels={selectedModels}
									bind:messageInput"""
    content = re.sub(pattern_ph, replacement_ph, content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Chat.svelte patched successfully.")

def patch_placeholder():
    filepath = 'src/lib/components/chat/Placeholder.svelte'
    print(f"Patching {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    content = normalize_newlines(content)
    
    # 1. remove export let activeButtonGroupId
    content = content.replace('export let activeButtonGroupId: string | null = null;', '')
    
    # 2. update MessageInput bind using regex
    pattern_mi = r'<MessageInput\s+bind:this=\{messageInput\}\s+bind:activeButtonGroupId\s+\{history\}\s+\{selectedModels\}'
    replacement_mi = """<MessageInput
					bind:this={messageInput}
					bind:selectedModels={selectedModels}
					{history}"""
    content = re.sub(pattern_mi, replacement_mi, content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Placeholder.svelte patched successfully.")

def patch_settings():
    filepath = 'src/lib/components/admin/Settings.svelte'
    print(f"Patching {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    content = normalize_newlines(content)
    
    # 1. remove import
    content = content.replace("import ButtonGroups from '../chat/Settings/ButtonGroups.svelte';", '')
    
    # 2. remove 'button-groups' from tab list using regex to handle spacing and trailing commas
    content = re.sub(r',\s*\'button-groups\'', '', content)
    content = re.sub(r'\'button-groups\'\s*,?', '', content)
    
    # 3. remove button-groups item from allSettings
    pattern_setting = r'\{\s*id:\s*\'button-groups\',[\s\S]*?\}'
    content = re.sub(pattern_setting, '', content)
    
    # 4. remove button-groups component mounting block
    pattern_mount = r'\{:else if selectedTab === \'button-groups\'\}\s*<ButtonGroups />'
    content = re.sub(pattern_mount, '', content)
    
    # Clean up trailing commas in lists
    content = content.replace(',\n\t]', '\n\t]')
    content = content.replace(',\n]', '\n]')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Settings.svelte patched successfully.")

if __name__ == '__main__':
    patch_message_input()
    patch_chat()
    patch_placeholder()
    patch_settings()
