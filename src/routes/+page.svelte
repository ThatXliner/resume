<script lang="ts">
	import me from '$lib/assets/profile.svg';
	import { gsap } from 'gsap';
	import Project from './Project.svelte';
	$effect(async () => {
		const { TextPlugin } = await import('gsap/TextPlugin');
		const { ScrollTrigger } = await import('gsap/ScrollTrigger');
		const { ScrollToPlugin } = await import('gsap/ScrollToPlugin');

		gsap.registerPlugin(TextPlugin, ScrollTrigger, ScrollToPlugin);
		const tl = gsap.timeline();

		tl.from('#intro .hero-content', { scale: 0.5, opacity: 0, duration: 0.5 }) //e
			.to('#intro #hello', {
				duration: 1,
				text: "Hi! I'm Bryan Hu",
				ease: 'none'
			});
		tl.to('#intro #bio', {
			duration: 1,
			text: 'Short bio',
			ease: 'none'
		});
		tl.from(
			'#intro #socials > a',
			{
				stagger: 0.5,
				duration: 1,
				opacity: 0
			},
			'<'
		);
		gsap.to('main', {
			backgroundColor: 'black',
			backgroundImage: 'none',

			scrollTrigger: {
				trigger: '#collab',
				end: 'top center-=10%',
				scrub: true
			}
		});
		gsap.from('#card-fly-right', {
			x: '100vw',
			duration: 1,
			scrollTrigger: {
				trigger: '#card-fly-right',
				start: 'top center'
			}
		});
		gsap.from('#card-fly-left', {
			x: '-100vw',
			duration: 1,
			scrollTrigger: {
				trigger: '#card-fly-left',
				start: 'top center'
			}
		});
	});
	// const picturesOfMe = import.meta.glob('$lib/assets/me_*.{png,jpg}', { eager: true });
</script>

<main class="orange-bg overflow-x-hidden" data-theme="light">
	<section id="intro" class="hero min-h-screen">
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
				<h1 class="text-5xl font-bold" id="hello" />
				<p class="py-6" id="bio" />
				<!-- Social icons -->
				<div class="flex-row" id="socials">
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
				<button
					class="btn btn-primary"
					id="see-more"
					on:click={() => {
						gsap.to(window, {
							duration: 0.5,
							scrollTo: '#collab',
							ease: 'power2.inOUt',
							onComplete: () => {
								window.location.hash = '#collab';
							}
						});
					}}
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
	</section>
	<section id="collab" class="min-h-screen py-11 bg-black flex flex-col" data-theme="dark">
		<div class="w-full flex-col">
			<h2 class="text-6xl font-bold mx-[10%] mt-6">
				Here are some projects that I made in <span
					class="blue-gradient moving-gradient gradient-text">collaboration</span
				> with others
			</h2>
			<div class="flex flex-col pt-[15rem]">
				<Project from="left" />
				<Project from="right" />
				<!-- <Project from="left" />
				<Project from="right" /> -->
			</div>
		</div>
	</section>
</main>

<style>
	.gradient-text {
		background-clip: text !important;
		color: transparent;
	}
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
	.blue-gradient {
		background: rgb(65, 89, 217);
		background: linear-gradient(
			90deg,
			rgba(65, 89, 217, 1) 0%,
			rgba(82, 119, 210, 1) 25%,
			rgba(20, 131, 232, 1) 50%,
			rgba(82, 119, 210, 1) 75%,
			rgba(65, 89, 217, 1) 100%
		);
	}
	.moving-gradient {
		background-size: 200% 100%; /*Adjust the width as needed*/

		animation: move-gradient 2s linear infinite;
	}

	@keyframes move-gradient {
		0% {
			background-position: -100% 50%;
		}
		100% {
			background-position: 100% 50%;
		}
	}
</style>
