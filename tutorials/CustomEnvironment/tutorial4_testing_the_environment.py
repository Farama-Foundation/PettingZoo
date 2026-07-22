from tutorial2_adding_game_logic import CustomEnvironment
from tutorial3_action_masking import CustomActionMaskedEnvironment

from pettingzoo import make, parallel_registry, register
from pettingzoo.test import parallel_api_test

if __name__ == "__main__":
    # Sanity check
    env = CustomEnvironment()
    parallel_api_test(env, num_cycles=1_000_000)

    env = CustomActionMaskedEnvironment()
    parallel_api_test(env, num_cycles=1_000_000)

    # Register custom environments so they can be created with make()
    register("parallel", "custom/custom_environment-v0", CustomEnvironment)
    register(
        "parallel",
        "custom/custom_action_masked_environment-v0",
        CustomActionMaskedEnvironment,
    )

    # Confirm the environments are available in the parallel registry
    assert "custom/custom_environment-v0" in parallel_registry
    assert "custom/custom_action_masked_environment-v0" in parallel_registry

    # Environments can now be created via make, just like built-in ones
    env = make("parallel", "custom/custom_environment-v0")
    parallel_api_test(env, num_cycles=1_000_000)

    env = make("parallel", "custom/custom_action_masked_environment-v0")
    parallel_api_test(env, num_cycles=1_000_000)
