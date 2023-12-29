<script>
	import me from '$lib/assets/profile.svg';
	// const picturesOfMe = import.meta.glob('$lib/assets/me_*.{png,jpg}', { eager: true });
</script>

<div class="hero min-h-screen orange-bg">
	<div class="hero-content w-full flex-col lg:flex-row justify-center">
		<!-- <div class="h-96 w-96 carousel rounded-box shadow-2xl">
			{#each Object.keys(picturesOfMe) as me}
				<div class="carousel-item w-96 overflow-clip">
					<img src={me} class="object-cover" alt="Me" />
				</div>
			{/each}
		</div> -->
		<img src={me} class="h-46 w-46 rounded-box shadow-2xl" alt="My profile icon" />
		<div>
			<h1 class="text-5xl font-bold">Hi! I'm Bryan Hu</h1>
			<p class="py-6">Short bio</p>
			<!-- Social icons -->
			<div class="flex-row">
				<a href="https://github.com/ThatXliner" class="inline-block text-5xl i-mdi-github" />
				<a
					href="https://www.instagram.com/thatxliner/"
					class="inline-block text-5xl i-mdi-instagram"
				/>
				<a
					href="https://www.linkedin.com/in/thatxliner/"
					class="inline-block text-5xl i-mdi-linkedin"
				/>
			</div>
			<!-- Fade to black to transition to what i made -->
			<button class="btn btn-primary"
				>See more <svg
					xmlns="http://www.w3.org/2000/svg"
					fill="none"
					viewBox="0 0 24 24"
					stroke-width="1.5"
					stroke="currentColor"
					class="w-6 h-6"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						d="M17.25 8.25L21 12m0 0l-3.75 3.75M21 12H3"
					/>
				</svg>
			</button>
		</div>
	</div>
</div>

<style>
	.orange-bg {
		background-color: hsla(22, 93%, 71%, 1);
		background-image: radial-gradient(at 35% 49%, hsla(58, 100%, 50%, 0.72) 0px, transparent 50%),
			radial-gradient(at 40% 20%, hsla(28, 100%, 74%, 1) 0px, transparent 50%),
			radial-gradient(at 0% 50%, hsla(355, 100%, 93%, 1) 0px, transparent 50%),
			radial-gradient(at 80% 50%, hsla(340, 100%, 76%, 1) 0px, transparent 50%),
			radial-gradient(at 0% 100%, hsla(22, 100%, 77%, 1) 0px, transparent 50%),
			radial-gradient(at 87% 93%, hsla(242, 100%, 70%, 1) 0px, transparent 50%),
			radial-gradient(at 0% 0%, hsla(343, 100%, 76%, 1) 0px, transparent 50%);
	}
</style>
