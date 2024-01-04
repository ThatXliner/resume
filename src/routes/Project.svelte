<script lang="ts">
	const { from } = $props<{ from: 'left' | 'right' }>();
</script>

<div class="h-[50vh] mx-[15vw] m{from.charAt(0)}-auto" id="card-fly-{from}">
	<div class="card w-96 bg-base-100 shadow-xl">
		<figure>
			<img
				src="https://daisyui.com/images/stock/photo-1606107557195-0e29a4b5b4aa.jpg"
				alt="Shoes"
			/>
		</figure>
		<div class="card-body">
			<h2 class="card-title">Shoes!</h2>
			<p>If a dog chews shoes whose shoes does he choose?</p>
			<div class="card-actions justify-end">
				<button class="btn btn-primary">Buy Now</button>
			</div>
		</div>
	</div>
</div>
