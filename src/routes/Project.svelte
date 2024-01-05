<script lang="ts">
	import { onMount } from 'svelte';

	const { from, repo } = $props<{
		from: 'left' | 'right';
		repo: string;
		// repo:  extends `${infer Owner}/${infer Repo}`;
	}>();
	const [owner, name] = repo.split('/');
	const QUERY = `query {
  repository(owner: "${owner}", name: "${name}") {
    description
    url
    homepageUrl
    languages(first: 5) {
      nodes {
        name
      }
    }
    
  }
}`;
	let data = $state<{
		repository: {
			description: string;
			url: string;
			homepageUrl: string;
			languages: {
				nodes: {
					name: string;
				}[];
			};
		};
	}>({ repository: { description: '', url: '', homepageUrl: '', languages: { nodes: [] } } });
	onMount(async () => {
		const res = await fetch('/github', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				Accept: 'application/json'
			},
			body: JSON.stringify({ query: QUERY })
		});
		const json = await res.json();
		data = json.data;
	});
</script>

<div class="h-[50vh] {from === 'left' ? 'ml-auto' : 'mr-auto'}" id="card-fly-{from}">
	<div class="card w-96 bg-base-100 shadow-xl">
		<figure>
			<img
				src="https://daisyui.com/images/stock/photo-1606107557195-0e29a4b5b4aa.jpg"
				alt="Shoes"
			/>
		</figure>
		<div class="card-body">
			<h2 class="card-title">{repo}</h2>
			<p>{data.repository.description}</p>
			<div class="card-actions">
				<a href={data.repository.url} class="inline-block text-5xl i-mdi-github" />
				<a href={data.repository.homepageUrl} class="inline-block text-5xl i-mdi-home" />
				<!-- We  -->
			</div>
		</div>
	</div>
</div>
